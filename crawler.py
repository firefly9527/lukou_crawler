import requests
from requests.models import parse_url
import errors
from bs4 import BeautifulSoup
from bs4.element import Tag
import pandas
from log import log
import configs


class LukouCrawler():
    def __init__(self):
        self.session = requests.Session()
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
            'Host': 'www.lukou.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
        }
        self.session.headers = headers
        self.base_url = 'http://www.lukou.com'
        self.search_url = 'http://www.lukou.com/search'

    def crawle(self, keywords, pages, start_page, search_type, sort_type):
        '''
        search_type: 0:宝贝, 1:文章, 3:专辑, 4:团购
        sort_type: 0:默认排序, 3:最新发布, 4:最热排序
        '''
        all_data = []
        page = start_page
        end_page = page + pages
        referer = self.base_url
        retry_count = 0
        while page < end_page:
            try:
                log.info(f'爬取第{page}页')
                html, url = self.crawle_page(keywords,
                                             referer,
                                             page-1,
                                             search_type,
                                             sort_type)
                log.debug(f'解析第{page}页')

                data, next = self.parse_page(html)
                log.info('解析出{}条商品信息'.format(len(data)))
                all_data.extend(data)
                if next:
                    retry_count = 0
                    page += 1
                    referer = url
                else:
                    break
            except Exception as err:
                log.warning(f'爬取第{page}页失败', exc_info=True)
                if retry_count < 3:
                    retry_count += 1
                else:
                    retry_count = 0
                    page += 1
        dataset = pandas.DataFrame(all_data)
        return dataset

    def crawle_page(self, keywords, referer, page, search_type, sort_type):
        headers = {
            'Referer': referer or self.base_url
        }
        params = {
            'q': keywords,
            's': search_type,
            'page': page,
            'sort': sort_type
        }
        content = self._crawle_page(headers, params)
        return content

    def _crawle_page(self, headers, params):
        resp = self.session.get(url=self.search_url,
                                headers=headers,
                                params=params,
                                timeout=configs.timeout)
        if resp.status_code != 200:
            raise errors.HTTPException
        return resp.text, resp.request.url

    def _parse_item(self, item):
        ret = {
            "author": None,
            "publish_time": None,
            "text": None,
            "title": None,
            "price": None,
            "sale_price": None,
            "comment": None,
            "forward": None,
            "praize": None,
            "collect": None,
            "feed_url": None
        }
        author_obj_content = item.find("div", class_="author").find_all("a")
        if author_obj_content:
            ret["author"] = author_obj_content[0].text
            ret["publish_time"] = author_obj_content[1].text
            ret["feed_url"] = author_obj_content[1].get("href")
        text_obj = item.find("div", class_="text")
        if text_obj:
            ret["text"] = text_obj.text.strip(' ') if text_obj else None

        # cmd-info
        cmd_info = item.find("div", class_="cmd-info")
        if cmd_info:
            title_obj = cmd_info.find("div", class_="cmd-title")
            ret["title"] = title_obj.text.strip(' ') if title_obj else None
            price_obj = cmd_info.find("div", class_="cmd-price")
            ret["price"] = price_obj.text if price_obj else None
            ret["sale_price"] = cmd_info.find(
                "div", class_='cmd-sale-price').find("b").text

        # feed-act
        feed_act = item.find("div", class_="feed-act")
        if feed_act:
            comment = feed_act.find("a", class_="feed-comment").find("b").text
            ret["comment"] = int(comment) if comment != '评论' else 0
            forward = feed_act.find("a", class_="feed-forward").find("b").text
            ret["forward"] = int(forward) if forward != '转发' else 0
            praize = feed_act.find("a", class_="feed-praize").find("b").text
            ret["praize"] = int(praize) if praize != '赞' else 0
            collect = feed_act.find("a", class_="feed-collect").find("b").text
            ret["collect"] = int(collect) if collect != '收藏' else 0

        return ret

    def parse_page(self, html):
        root = BeautifulSoup(html, 'lxml')

        result_list = root.find_all('div', class_='feed-wrap')
        data = [self._parse_item(
            i) for i in result_list if isinstance(i, Tag)]
        next_page_button_obj = root.find('a', class_="next")
        next_page_button_status = bool(next_page_button_obj.get(
            'href')) if next_page_button_obj else None
        return data, next_page_button_status
