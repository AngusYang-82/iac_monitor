__author__ = 'Angus Yang'

from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
Base = declarative_base()


class ProxyInfo(Base):
    '''定义代理信息表，IP，type，port，所属site以及自定义代理名称
    '''
    __tablename__ = 'proxy_info'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    proxy_ip = Column(String(64), nullable=False)
    proxy_type = Column(String(64), nullable=False)
    proxy_port = Column(String(64), nullable=False)
    proxy_site = Column(String(64), nullable=False)
    proxy_name = Column(String(64), nullable=False)

    def __init__(self, proxy_ip, proxy_type, proxy_port, proxy_site, proxy_name):
        self.proxy_ip = proxy_ip
        self.proxy_type = proxy_type
        self.proxy_port = proxy_port
        self.proxy_site = proxy_site
        self.proxy_name = proxy_name


class ProxyCheckresult(Base):
    '''定义代理检查结果存储表，No（外键，proxy_info表id，status状态，response time，以及检查时间
    '''
    __tablename__ = 'proxy_checkresult'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    proxy_No = Column(Integer, ForeignKey('proxy_info.id'), nullable=False)
    proxy_status = Column(Integer, nullable=False)
    proxy_rt = Column(DECIMAL(10, 2), nullable=False)
    checktime = Column(DateTime, nullable=False)

    def __init__(self, proxy_No, proxy_status, proxy_rt, checktime):
        self.proxy_No = proxy_No
        self.proxy_status = proxy_status
        self.proxy_rt = proxy_rt
        self.checktime = checktime


class UseDB(object):
    """数据库初始类"""

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self._mysqlconfig = self.kwargs['mysqlconfig']
        self._engine = create_engine(self._mysqlconfig)
        Base.metadata.create_all(self._engine)
        sess = sessionmaker(bind=self._engine)
        self.session = sess()

    def disconnect(self):
        self.session.close()
        self._engine.dispose()
