__author__ = 'Angus Yang'


import requests
from model.db import UseDB, ProxyInfo, ProxyCheckresult
import os


def struc_proxies(ip, port, type):
    proxies = {
        'http': '{}://{}:{}'.format(type, ip, port),
        'https': '{}://{}:{}'.format(type, ip, port)
    }
    return proxies


def req_value(url, method='GET', proxies=None, timeout=8):
    '''获取网站访问指标'''
    with requests.Session() as sess:
        sess.proxies = proxies
        s = sess.request(method=method, url=url,
                         proxies=proxies, timeout=timeout)
        return dict(req_status=s.status_code, req_rptime=s.elapsed.total_seconds()*1000)


def set_logging(loggername, file_path=None):
    if file_path == None:
        file_path = os.getenv("HOME")+'/proxy_check.log'
    else:
        file_path = file_path
    import logging
    logger = logging.getLogger(loggername)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    file_handler = logging.FileHandler(file_path)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger
