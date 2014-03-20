#!/usr/bin/python2.7
# encoding: utf-8

import sys
import os
import logging
import traceback
import argparse
import re
import shutil
import glob
from ConfigParser import RawConfigParser

__version__ = 0.1

def _find_master():
	master_files = sorted(glob.glob('/etc/php/cgi-php*/php.ini'), reverse=True)

	if master_files:
		return master_files[0]

	raise Exception('No master php.ini found')

def merge(master, updates, outfile, **kwargs):
	if not master:
		master = _find_master()

	if not isinstance(updates, (list, tuple)):
		updates = [updates]

	print "Merging files: %s and %s" % (master, ', '.join(updates))

	parser = RawConfigParser()
	parser.read(updates)

	with open(master, 'r') as orig:
		with open(outfile, 'w') as new:
			current_section=None
			for line in orig:
				sec_m = re.match("^\[([\w\d_\-\s]+)\]\s*", line, re.IGNORECASE)
				if sec_m:
					current_section=sec_m.group(1)
					new.write(line)
				else:
					if not parser.has_section(current_section):
						new.write(line)
						continue

					var_m = re.match("^(?:;)?([\w\d\_\-\.]+)\s*=\s*(.*)\n$", line, re.IGNORECASE)
					if var_m:
						key, value = var_m.groups()

						if parser.has_option(current_section, key):
							new_value = parser.get(current_section, key)
#							print "REPLACING: %s = %s with value %s" % (key, value, new_value)
							new.write("%s = %s\n" % (key, new_value % kwargs))
							parser.remove_option(current_section, key)

							if not parser.items(current_section):
								parser.remove_section(current_section)
						else:
							new.write(line)

					else:
						new.write(line)

			if parser.sections():
				#print "The following values were not set:"
				for s in parser.sections():
					new.write("")
					new.write("[%s]\n" % s)
					for t in parser.items(s):
						new.write("%s = %s\n" % t)

		

def main(argv=None):
	try:
		parser = argparse.ArgumentParser(description='Merges the changes from the two given ini-style files into one.')
		parser.add_argument('file', metavar='file', nargs='+', help='The files to merge')

		parser.add_argument('-m', '--master', dest="master", default=None,
							help="Use the given master file (default: autodetect)")

		parser.add_argument('-o', '--outfile', dest="outfile", required=True,
							help="Write output to OUTFILE")

		parser.add_argument("-v", "--vhost-dir", dest="vhost_dir", default="", required=True)

		args = parser.parse_args()

		merge(args.master, args.file, args.outfile, vhost_dir=args.vhost_dir)

	except Exception, e:
		logging.error(e)
		logging.error(traceback.format_exc())
		return 2

if __name__ == "__main__":
	sys.exit(main())
