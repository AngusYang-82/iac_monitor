__author__ = 'Angus Yang'


from model.model import set_logging
from model.model import req_value, struc_proxies
from model.db import UseDB, ProxyCheckresult, ProxyInfo
import requests
import time
import datetime
import json
import yaml

logger = set_logging(__name__)

stream = open('config.yaml', 'r')
config = yaml.load(stream)
mysql_config = "mysql+pymysql://{}:{}@{}/{}".format(config['mysql_user'], config['mysql_password'],
                                                    config['mysql_host'], config['mysql_db'])
check_site = config['check_site']
send_opagent = config['send_opagent']
opagent_url = config['opagent_url']
check_url = config['check_url']


def stuctproxiesinfo(mysqlconfig, proxy_site=check_site):
    try:
        conn = UseDB(mysqlconfig=mysqlconfig)
        sess = conn.session

        if proxy_site == 'all':
            results = sess.query(ProxyInfo).all()
        else:
            results = sess.query(ProxyInfo).filter_by(
                proxy_site=proxy_site).all()

        proxiesinfo = list()

        for result in results:
            proxyinfo = dict(
                proxy_id=result.id,
                proxy_ip=result.proxy_ip,
                proxy_type=result.proxy_type,
                proxy_port=result.proxy_port,
                proxy_site=result.proxy_site,
                proxies=struc_proxies(
                    result.proxy_ip, result.proxy_port, result.proxy_type)
            )
            proxiesinfo.append(proxyinfo)
        sess.close()
        conn.disconnect()
        return proxiesinfo
    except Exception as e:
        logger.error('Struc proxy info occur error {}'.format(e))


def multi_check(object):

    try:
        req = req_value(check_url, proxies=object['proxies'])
        proxy_status = 0
        req_rptime = req['req_rptime']
    except Exception as e:
        logger.error('Proxy {} did occur error'.format(object['proxy_ip']))
        proxy_status = 1
        req_rptime = 8000

    ts = int(time.time())
    metric = object['proxy_ip'] + ':' + object['proxy_port']
    payload = [
        {
            "endpoint": object['proxy_site'] + '_proxy_status',
            "metric": metric,
            "timestamp": ts,
            "step": 30,
            "value": proxy_status,
            "counterType": "GAUGE",
            "tags": "",
        },

        {
            "endpoint": object['proxy_site'] + '_proxy_status',
            "metric": metric,
            "timestamp": ts,
            "step": 30,
            "value": req_rptime,
            "counterType": "GAUGE",
            "tags": "",
        },
    ]

    try:
        conn = UseDB(mysqlconfig=mysql_config)
        sess = conn.session
        checkresult = ProxyCheckresult(
            object['proxy_id'], proxy_status, req_rptime, datetime.datetime.now())
        sess.add(checkresult)
        sess.commit()
        sess.close()
        conn.disconnect()
        logger.info('{}(port:{}, type:{}) check result has insert table'.format(
            object['proxy_ip'], object['proxy_port'], object['proxy_type']))
    except Exception as e:
        logger.error('proxy {} check result save database occur error.{}'.format(
            object['proxy_ip'], e))

    if send_opagent == True:
        try:
            r = requests.post(opagent_url, data=json.dumps(payload), timeout=5)
            logger.info('{}(port:{}, type:{}) check result has sended openfalcon'.format(
                object['proxy_ip'], object['proxy_port'], object['proxy_type']))
        except Exception as e:
            logger.error('{} send to openfalcon occur error {}'.format(
                object['proxy_ip'], e))


if __name__ == '__main__':

    try:
        proxiesinfo = stuctproxiesinfo(mysql_config)
    except Exception as e:
        logger.error('Get proxy info from database occur error : {}'.format(e))

    from multiprocessing import Pool
    p = Pool(8)
    p.map(multi_check, proxiesinfo)
