from datetime import datetime, timedelta
import pickle
from sqlalchemy import create_engine, Table, MetaData, Column, String, Integer, DateTime
from sqlalchemy.exc import OperationalError

from settings import database, last_seen_delta


def get_host_shortname(host):
    if host.endswith('.fritz.box'):
        shortname = host.partition('.')[0]
    else:
        shortname = host
    return shortname


def get_database():
    db = create_engine(database, pool_recycle=6 * 3600)
    metadata = MetaData(db)
    log = Table(
        'host_log',
        metadata,
        Column('hostname', String(256), primary_key=True),
        Column('status', Integer),
        Column('timestamp', DateTime, primary_key=True),
        Column('ipv4', String(32)),
        Column('ipv6', String(256)),
    )
    try:
        log.create()
    except Exception:
        # import traceback
        # traceback.print_exc()
        pass
    return log


def get_homedump():
    try:
        with open('homedump.pkl', 'rb') as dumpfile:
            homedump = pickle.load(dumpfile)
        return homedump
    except Exception as e:
        import traceback

        traceback.print_exc()
        print('file not found', e)
        return {}


def get_status():
    now = datetime.utcnow()
    homedump = get_homedump()
    result = dict()
    for host, last_seen in homedump.items():
        result[host] = now - last_seen
    return result


def get_active_hosts(homedump):
    hosts = []
    now = datetime.utcnow()
    for host, last_seen in sorted(homedump.items()):
        if now - last_seen < timedelta(minutes=last_seen_delta - 2):
            hosts.append(host)
    return sorted(hosts)
