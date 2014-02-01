#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import argparse
import time
import os

def send(api_token, recipient, subject, message):
	msg = "<no text>"
	data = {
		'token': api_token,
		'user': args.recipient,
		'priority': 1,
		'sound': 'pushover',
		'title': subject,
		'message': message,
	}	
	url = "https://api.pushover.net/1/messages.json"
	u = urllib2.urlopen(url, urllib.urlencode(data))


if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('-a', '--api-token', help="The application's api key", required=True)
	parser.add_argument('-r', '--recipient', help="User or Group api key", required=True)
	parser.add_argument('args', nargs=argparse.REMAINDER)

	event = os.environ.get('NOTIFYTYPE', 'unknown event')
	args = parser.parse_args()
	send(args.api_token, args.recipient, 'USV: %s' % event, ' '.join(args.args))
