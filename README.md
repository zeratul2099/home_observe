# home_observe
A small python daemon which observes the home network and sends a notification, if a new host joins the network.
It repeatedly make a 'nmap -sP -PR'-network scan and memorizes all found hosts. If a new host is found, it sends
a notification via notifymyandroid. Found hosts will not be scanned for 14 minutes (configurable). This is neccassary
due most mobile devices will experience a massive battery drain if pinged every few seconds. Hosts, which were away
for more than 15 minutes (configurable) will considered a new, and a new notification is send on reappear.
Hosts a recognized by the first part of their full network name (e.g. host1.fritz.box is recognized as host1).


Dependencies:
- python2
- nmap
- pynma

Note: home_observe must run as root due to network scans done by nmap


Installation:

- Set up a account at https://notifymyandroid.com/ and generate an api-key.
- Copy settings_example.py to settings.py and edit it according your needs, including the nma-api-key.
- Install pynma from https://github.com/uskr/pynma.git in your PYTHONPATH or copy pynma.py to the home_observe directory
- 'sudo python2 home_observe.py'


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
  - python 3
  - notification on network leave
  - add setup.py

