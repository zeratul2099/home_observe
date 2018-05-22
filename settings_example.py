
# e.g. 192.168.178.1-150
network = ''

# get from pushover.net
pa_app_token = ''
pa_user_key = ''

# limit of a host must be offline/away to be notified again when comming online. In minutes
last_seen_delta = 15

# also notify if device goes offline (not seen in the <last_seen_delta> minutes)
notify_offline = True

# do not notify about this hosts
notify_blacklist = [ '']

# database for logging
database = 'sqlite:///home_observe.db'
