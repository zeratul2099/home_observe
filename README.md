# home_observe
A small python daemon which observes the home network and sends a notification, if a new host joins the network.
It repeatedly make a 'nmap -sP -PR'-network scan and memorizes all found hosts. If a new host is found, it sends
a notification via pushover (pushover.net). Found hosts will not be scanned for 14 minutes (configurable). This is neccassary
due most mobile devices will experience a massive battery drain if pinged every few seconds. Hosts, which were away
for more than 15 minutes (configurable) will considered a new, and a new notification is send on reappear.
Hosts are recognized by their full network name (e.g. host1.fritz.box). Notification only contain the first part
of the network name (e.g. host1).
Optionally, a notification is send if a host goes offline / is not seen for 15 minutes.

Dependencies:
- python3
- nmap
- sqlalchemy
- flask
- pytz
- requests

Note: home_observe must run as root due to network scans done by nmap


Installation:

- Set up a account at https://pushover.net/ and generate an app-token.
- Copy settings_example.py to settings.py and edit it according your needs, including the pushover app-token and user-key.
- 'sudo python3 home_observe.py -d'


Usage: home_observe.py [-h] [-d] [-s] [-a] [--sleep SLEEP]

HereObserve, a local network observer

optional arguments:
  -h, --help     show this help message and exit
  
  -d, --daemon   daemon mode
  
  -s, --status   print status and exit
  
  -a, --active   print active hosts and exit
  
  --sleep SLEEP  sleep after every scan (in seconds)
  
  
  Planned features:
  - additional notification services (e.g. mail)
  - add setup.py
  - webgui
    - paging
    - plots
    - sorting

