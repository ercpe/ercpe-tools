#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import argparse
import time


def send(args):
	msg = "<no text>"
	data = {
		'token': args.api_token,
		'user': args.recipient,
		'priority': 1,
		'timestamp': args.timestamp,
		'sound': args.sound
	}

	if args.type == "host":
		data['title'] = "%s is %s" % (args.host_alias, args.host_state)
		msg = '%s (%s) is %s: %s' % (args.host_alias, args.host_address, args.host_state, args.host_output)
	elif args.type == "service":
		data['title'] = "%s: %s is %s" % (args.host_alias, args.service_description, args.service_state)
		msg = '%s on %s (%s) is %s: %s' % (args.service_description, args.host_alias, args.host_address, args.service_state, args.service_description)


	data['message'] = msg

	url = "https://api.pushover.net/1/messages.json"
	u = urllib2.urlopen(url, urllib.urlencode(data))

if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('-a', '--api-token', help="The application's api key", required=True)
	parser.add_argument('-r', '--recipient', help="User or Group api key", required=True)
	parser.add_argument('-t', '--type', choices=['host', 'service'], help="Notification type", required=True)
	parser.add_argument('-s', '--sound', default="pushover", help="Use SOUND instead of the default ('pushover')")

	parser.add_argument('--notification-type', help="Nagios notification type (PROBLEM, RECOVERY, ACKNOWLEDGEMENT)")
	parser.add_argument('--timestamp', help="Notification timestamp (from Nagios' $TIMET$ macro)", default=int(time.time()))
	parser.add_argument('--url', help="Action URL (typically from Nagios' $SERVICEACTIONURL$ or $HOSTACTIONURL$ macro)")

	parser.add_argument('--host-alias', required=True)
	parser.add_argument('--host-state')
	parser.add_argument('--host-address')
	parser.add_argument('--host-output')

	parser.add_argument('--service-state')
	parser.add_argument('--service-output')
	parser.add_argument('--service-description')

	send(parser.parse_args())