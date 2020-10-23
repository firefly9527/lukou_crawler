import datetime
from crawler import LukouCrawler
import click
import dataset_processer


@click.command()
@click.argument('keywords', nargs=-1)
@click.option('--pages', '-P', default=1, help='page')
@click.option('--start-page', '-S', default=1, help='start page')
@click.option('--search-type', '-T', default=0, help='search_type: 0:宝贝, 1:文章, 3:专辑, 4:团购')
@click.option('--sort-type', '-t', default=0, help='sort_type: 0:默认排序, 3:最新发布, 4:最热排序')
def main(keywords, pages, start_page, search_type, sort_type):
    keywords = ' '.join(keywords)
    if not keywords:
        raise ValueError
    start_time_str = str(datetime.datetime.now().replace(
        microsecond=0)).replace(':', '-')
    crawler = LukouCrawler()
    result = crawler.crawle(keywords,
                            pages,
                            start_page,
                            search_type,
                            sort_type)

    result['feed_url'] = result['feed_url'].apply(
        dataset_processer.generate_excel_hyperlink)
    result = dataset_processer.filter_column(result)

    result.to_excel(f'{keywords} {start_time_str}.xlsx',
                    index=False,
                    encoding='gb18030')


if __name__ == "__main__":
    main()
