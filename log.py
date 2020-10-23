# encoding:utf-8

import logging

log=None

def init_logger(debug=False):
    global log
    if not log:
        formatter=logging.Formatter(fmt= '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s', datefmt = '%y%m%d %H:%M:%S')
        handler=logging.StreamHandler()
        handler.setFormatter(formatter)
        logger=logging.getLogger(__name__)
        logger.addHandler(handler)
        log=logger
    if debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)


init_logger()

def query_log(msg,resp,func=None,suffix='',*args,**kwargs):
    if func:
        tmp=func(resp)
        if resp.status_code==200 and func(resp):
            msg=msg+' '+'success'
            log.info(msg+suffix)
    elif resp.status_code==200:
            msg=msg+' '+'success'
            log.info(msg+suffix)
    else:
        msg=msg+' '+'success'
        log.warn(msg+suffix)

if __name__ == '__main__':
    log.info('log test info')
    log.debug('log test debug')
    init(debug=True)
    log.info('log test info')
    log.debug('log test debug')
    init(debug=False)
    log.info('log test info')
    log.debug('log test debug')