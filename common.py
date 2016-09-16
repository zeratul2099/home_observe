
from sqlalchemy import create_engine, Table, MetaData, Column, String, Integer, DateTime
from sqlalchemy.exc import OperationalError

from settings import database


def get_host_shortname(host):
    if host.endswith('.fritz.box'):
        shortname = host.partition('.')[0]
    else:
        shortname = host
    return shortname


def get_database():
    db = create_engine(database)
    metadata = MetaData(db)
    log = Table('log', metadata,
                Column('hostname', String, primary_key=True),
                Column('status', Integer),
                Column('timestamp', DateTime, primary_key=True),
                Column('ipv4', String),
                Column('ipv6', String),
                )
    try:
        log.create()
    except OperationalError:
        # import traceback
        # traceback.print_exc()
        pass
    return log
