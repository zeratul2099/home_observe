# home_observe
a small python daemon which observes the home network and sends a notification, if a new host joins the network.

Installation:

- Set up a account at https://notifymyandroid.com/ and generate an api-key.
- Copy settings_example.py to settings.py and edit it according your needs, including the nma-apt-key.
- Install pynma from https://github.com/uskr/pynma.git in your PYTHONPATH or copy pynma.py to the home_observe directory
- 'python2 home_observe.py'


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
  
