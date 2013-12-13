#!/usr/bin/python3
# encoding: utf-8

import sys
import traceback
import argparse
import re
from sh import arp #@UnusedImport @UnresolvedImport

def scan(allowed):
	output = arp('-n').strip().split('\n')

	good = {}
	bad = {}

	for line in output:
		ip, hwtype, mac, flags, iface = tuple(re.split('\s\s+', line.lower()))
		
		if ip == 'address':
			continue

		#print("Found %s with %s on %s" % (mac, ip, iface))
		
		if mac in allowed:
			good[mac] = ip
		else:
			bad[mac] = ip
	
	print("Good answers:")
	
	for mac, ip in good.items():
		print("%s: (%s)" % (mac, good[mac]))

	print("\n\nBAD ANSWERS:")
	for mac, ip in bad.items():
		print("%s (%s)" % (mac, ip))


def main(argv=None):
	'''Command line options.'''
	
	if argv is None:
		argv = sys.argv[1:]

	try:
		parser = argparse.ArgumentParser(description='Some cool tool.')
		parser.add_argument('--allowed-file', '-a', help="File with allowed mac/label pairs")
		
		args = parser.parse_args()


		allowed = {}
		with open(args.allowed_file, 'r') as f:
			for line in [x.strip() for x in f.readlines()]:
				if not line:
					continue

				chunks = re.split('\s+', line)
				allowed[chunks[0].lower()] = chunks[1] if len(chunks) > 1 else chunks[0]
		
		scan(allowed)

	except Exception as e:
		print(e)
		print(traceback.format_exc())
		return 2

if __name__ == "__main__":
	sys.exit(main())