import os
import time
from datetime import datetime, timedelta
import argparse
import pickle

import pynma

from settings import network, last_seen_delta, nma_api_key, notify_offline

offline_notified = set()


def get_homedump():
    try:
        with open('homedump.pkl') as dumpfile:
            homedump = pickle.load(dumpfile)
        return homedump
    except Exception, e:
        import traceback
        traceback.print_exc()
        print 'file not found', e
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
    for host, last_seen in homedump.iteritems():
        result += '%s:\n\t%s\n' %(host, now - last_seen)
    return result

def home():
    now = datetime.utcnow()
    global offline_notified
    print 'offline notified', offline_notified
    homedump = get_homedump()
    excluded_hosts = get_active_hosts(homedump)
    if excluded_hosts:
        nmap_command = 'nmap -sP -PR --exclude %s %s' % (','.join(excluded_hosts), network)
    else:
        nmap_command = 'nmap -sP -PR %s' % network
    print nmap_command
    result = os.popen(nmap_command)
    notify_list = []
    seen_hosts = []
    for line in result.readlines():
        if 'done' in line:
            print line
        if 'scan report' in line:
            print line
            host = line.split(' ')[4]
            last_seen = homedump.get(host, datetime(1970,1,1,0,0))
            seen_hosts.append(host)
            ago = now - last_seen
            print '%s last seen %s ago' % (host, now - last_seen)
            if ago > timedelta(minutes=last_seen_delta):
                print 'NOTIFY', host
                try:
                    offline_notified.remove(host)
                except KeyError:
                    pass
                notify_list.append('%s (%s)' % (host.partition('.')[0], ago))
            homedump[host] = now
    notify_offline_list = []
    for host, last_seen in homedump.items():
        ago = now - last_seen
        if ago > timedelta(minutes=last_seen_delta) and ago < timedelta(minutes=last_seen_delta + 1):
            if host not in offline_notified:
                print 'NOTIFY OFFLINE', host
                notify_offline_list.append(host.partition('.')[0])
                offline_notified.add(host)
    if len(notify_list) > 0 or len(notify_offline_list) > 0:
        p = pynma.PyNMA(nma_api_key)
        # TODO add retry here
        if len(notify_list) > 0:
            p.push('HomeObserve', 'New devices online', ', '.join(notify_list))
        if len(notify_offline_list) > 0 and notify_offline is True:
            p.push('HomeObserve', 'Devices offline', ', '.join(notify_offline_list))
 
    with open('homedump.pkl', 'w') as dumpfile:
        pickle.dump(homedump, dumpfile)

    last_excluded_hosts = excluded_hosts

def main():
    parser = argparse.ArgumentParser(description='HomeObserve, a local network observer')
    parser.add_argument('-d', '--daemon', default=False, action='store_true', help='daemon mode')
    parser.add_argument('-s', '--status', default=False, action='store_true', help='print status and exit')
    parser.add_argument('-a', '--active', default=False, action='store_true', help='print active hosts and exit')
    parser.add_argument('--sleep', default=1, type=int, help='sleep after every scan (in seconds)')
    args = parser.parse_args()
    if args.active:
        print '\n'.join(get_active_hosts(get_homedump()))
        return
    if args.status:
        print get_status()
        return
    if args.daemon:
        while(True):
            home()
            time.sleep(args.sleep)
    else:
        home()

if __name__ == '__main__':
    main()
