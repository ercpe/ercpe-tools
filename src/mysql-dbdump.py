#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from argparse import ArgumentParser

import logging
import os
import datetime
import shlex
from subprocess import Popen, PIPE


class DatabaseDumper(object):

	def __init__(self, defaults_file, output_dir, format):
		self.defaults_file = defaults_file
		self.output_dir = output_dir
		self.format = format

	def list_databases(self):
		cmd = "mysql --defaults-file=%s --disable-column-names -b -s -e 'SHOW DATABASES;'" % self.defaults_file
		process = Popen(shlex.split(cmd), stdout=PIPE)
		out, _ = process.communicate()
		out = out.decode('unicode_escape')

		for db in (x.strip() for x in out.split('\n')):
			if db:
				yield db

	def dump_database(self, database, outfile):
		logging.debug("Dumping database '%s' to '%s'" % (database, outfile))

		cmd = "mysqldump --defaults-file=%s --disable-keys --skip-add-locks --quote-names --events --databases %s" % (self.defaults_file, database)

		with open(outfile, 'wb') as o:
			dump_process = Popen(shlex.split(cmd), stdout=PIPE)
			gzip_process = Popen(shlex.split("gzip -c - "), stdin=dump_process.stdout, stdout=o)
			dump_process.stdout.close()
			dump_process.wait()
			gzip_process.wait()

	def execute(self):
		if not os.path.exists(self.output_dir):
			os.makedirs(self.output_dir, 0o700)

		now = datetime.datetime.now()
		for database in self.list_databases():
			if database in ('lost+found', 'information_schema', 'performance_schema'):
				continue

			fargs = dict((x, getattr(now, x)) for x in ('day', 'month', 'year', 'hour', 'minute', 'second'))
			fargs['name'] = database
			filename = self.format % fargs

			outfile = os.path.join(self.output_dir, filename)
			self.dump_database(database, outfile)


if __name__ == '__main__':
	parser = ArgumentParser(description='MySQL dump helper')
	parser.add_argument('-c', '--defaults-file', required=True, help='Path to a mysql defaults file')
	parser.add_argument('-o', '--output-dir', default='/var/backups/mysql', help='Output directory (default: %(default)s)')
	parser.add_argument('-f', '--format', default="%(name)s.sql.gz", help="Python format string for the output file names (default: %(default)s)")
	parser.add_argument('-v', '--verbose', action='count', help='Increase verbosity', default=2)

	args = parser.parse_args()

	logging.basicConfig(level=logging.FATAL - (10 * args.verbose), format='%(asctime)s %(levelname)-7s %(message)s')

	dumper = DatabaseDumper(args.defaults_file, args.output_dir, args.format)
	dumper.execute()
