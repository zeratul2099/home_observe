#!/usr/bin/env python3
import os
import time
import socket
from datetime import datetime, timedelta
import argparse
import pickle
import random

import pynma
from sqlalchemy import asc
from settings import network, last_seen_delta, nma_api_key, notify_offline
from common import get_host_shortname, get_database

offline_notified = set()


def get_addresses(host):
    try:
        ipv4 = socket.getaddrinfo(host, None, socket.AF_INET)[0][4][0]
    except socket.gaierror:
        ipv4 = ''
    try:
        ipv6_set = set()
        for ipv6_info in socket.getaddrinfo(host, None, socket.AF_INET6):
            ipv6_set.add(ipv6_info[4][0])
        ipv6 = ','.join(list(ipv6_set))
    except socket.gaierror:
        ipv6 = ''
    return ipv4, ipv6


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


def get_active_hosts(homedump):
    hosts = []
    now = datetime.utcnow()
    for host, last_seen in sorted(homedump.items()):
        if now - last_seen < timedelta(minutes=last_seen_delta-1):
            hosts.append(host)
    return sorted(hosts)


def get_status():
    now = datetime.utcnow()
    homedump = get_homedump()
    result = ''
    for host, last_seen in homedump.items():
        result += '%s:\n\t%s\n' %(host, now - last_seen)
    return result



def show_database_log(hostname=None):
    log = get_database()
    select = log.select().order_by(asc(log.c.timestamp))
    if hostname:
        select = select.where(log.c.hostname.contains(hostname))
    rows = select.execute()
    for row in rows.fetchall():
        entry = dict(
            shortname = get_host_shortname(row.hostname),
            status = '\033[92mOnline\033[0m' if row.status == 1 else '\033[91mOffline\033[0m',
            timestamp = row.timestamp.strftime('%d.%m.%Y %H:%M:%S'),
            ipv4 = row.ipv4,
            ipv6 = row.ipv6,
        )
        print('{shortname:20s}\t{status}\t{timestamp}\t{ipv4:15}\t{ipv6}'.format(**entry))


def send_message_retry(p, header, message, retries=3):

    for retry in range(retries):
        try:
            p.push('HomeObserve', header, message)
            break
        except socket.gaierror:
            print('retry')
            time.sleep(1)
            continue



def home(log):
    now = datetime.utcnow()
    global offline_notified


    print('offline notified', offline_notified)
    homedump = get_homedump()
    excluded_hosts = get_active_hosts(homedump)
    if excluded_hosts:
        nmap_command = 'nmap -sP -PR --exclude %s %s' % (','.join(excluded_hosts), network)
    else:
        nmap_command = 'nmap -sP -PR %s' % network
    print(nmap_command)
    result = os.popen(nmap_command)
    notify_list = []
    seen_hosts = []
    for line in result.readlines():
        if 'done' in line:
            print(line)
        if 'scan report' in line:
            print(line)
            host = line.split(' ')[4]
            last_seen = homedump.get(host, datetime(1970,1,1,0,0))
            seen_hosts.append(host)
            ago = now - last_seen
            print('%s last seen %s ago' % (host, now - last_seen))
            if ago > timedelta(minutes=last_seen_delta):
                print('NOTIFY', host)
                ipv4, ipv6 = get_addresses(host)
                insert = log.insert()
                insert.execute(hostname=host, status=1, timestamp=now, ipv4=ipv4, ipv6=ipv6)
                try:
                    offline_notified.remove(host)
                except KeyError:
                    pass
                notify_list.append('%s (%s)' % (get_host_shortname(host), ago))
            homedump[host] = now
    notify_offline_list = []
    for host, last_seen in homedump.items():
        ago = now - last_seen
        if ago > timedelta(minutes=last_seen_delta) and ago < timedelta(minutes=last_seen_delta + 1):
            if host not in offline_notified:
                print('NOTIFY OFFLINE', host)
                ipv4, ipv6 = get_addresses(host)
                insert = log.insert()
                insert.execute(hostname=host, status=0, timestamp=now, ipv4=ipv4, ipv6=ipv6)
                notify_offline_list.append(get_host_shortname(host))
                offline_notified.add(host)
    if len(notify_list) > 0 or len(notify_offline_list) > 0:
        p = pynma.PyNMA(nma_api_key)
        if len(notify_list) > 0:
            send_messsage_retry(p, 'New devices online', ', '.join(notify_list))
        
        if len(notify_offline_list) > 0 and notify_offline is True:
            if random.randint(0, 1) == 0:
                send_message_retry(p, 'Devices offline', ', '.join(notify_offline_list) + ' is off the grid')
            else:
                if len(notify_offline_list) == 1:
                    send_message_retry(p, 'Devices offline', ', '.join(notify_offline_list) + ' has left the building')
                else:
                    send_message_retry(p, 'Devices offline', ', '.join(notify_offline_list) + ' have left the building')

    with open('homedump.pkl', 'wb') as dumpfile:
        pickle.dump(homedump, dumpfile)

    last_excluded_hosts = excluded_hosts


def main():
    parser = argparse.ArgumentParser(description='HomeObserve, a local network observer')
    parser.add_argument('-d', '--daemon', default=False, action='store_true', help='daemon mode')
    parser.add_argument('-s', '--status', default=False, action='store_true', help='print status and exit')
    parser.add_argument('-a', '--active', default=False, action='store_true', help='print active hosts and exit')
    parser.add_argument('-l', '--log', default=False, action='store_true', help='print database log')
    parser.add_argument('-o', '--host', default=None, help='show only logs of host')
    parser.add_argument('--sleep', default=1, type=int, help='sleep after every scan (in seconds)')
    args = parser.parse_args()
    if args.active:
        print('\n'.join(get_active_hosts(get_homedump())))
        return
    if args.status:
        print(get_status())
        return
    if args.log:
        show_database_log(hostname=args.host)
        return
    if args.daemon:
        log = get_database()
        while(True):
            home(log=log)
            time.sleep(args.sleep)
    else:
        log = get_database()
        home(log=log)

if __name__ == '__main__':
    main()

