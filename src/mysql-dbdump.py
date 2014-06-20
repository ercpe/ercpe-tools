#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import logging
import os
import tarfile
import datetime
import re
import sys

class DatabaseDumper(object):
	filename_pattern_single = "{YEAR}-{MONTH}-{DAY}-{DATABASE}.sql"
	filename_pattern_all = "{YEAR}-{MONTH}-{DAY}-ALL.sql"
	
	def __init__(self, host, user, password, output_dir, one_file_per_database, compress, dump_opts):
		self.host = host
		self.user = user
		self.password = password
		self.seperate_databases = one_file_per_database
		self.compress = compress
		self.output_dir = output_dir
		self.dump_opts = dump_opts
	
	def get_db_names(self):
		connection = None
		cursor = None
		
		tables = []

		try:
			connection = MySQLdb.connect(self.host, self.user, self.password, 'mysql')
			
			cursor = connection.cursor()
			cursor.execute('SHOW DATABASES;')

			for row in cursor.fetchall():
				if not 'lost+found' in row[0]:
					tables.append(row[0])

			return tables
		finally:
			if cursor:
				cursor.close()
			if connection:
				connection.close()

	def dump_database(self, database, outfile):
		logging.debug("Dumping database '%s' to '%s'" % (database, outfile))

		cmd = "/usr/bin/mysqldump"
		cmdargs = "-u %s --password=%s -h %s --disable-keys --skip-add-locks --quote-names --events --databases %s %s -r %s" % (self.user, self.password, self.host, database, self.dump_opts, outfile)

		os.system("%s %s" % (cmd, cmdargs))

	def dump_all_databases(self, outfile):
		logging.debug("Dumping all databases '%s'" % outfile)

		cmd = "/usr/bin/mysqldump"
		cmdargs = "-u %s --password=%s -h %s --disable-keys --skip-add-locks --quote-names --events -A %s -r %s" % (self.user, self.password, self.host, self.dump_opts, outfile)

		os.system("%s %s" % (cmd, cmdargs))

	def compress_file(self, infile, outfile):
		out = None
		try:
			out = tarfile.TarFile.open(outfile, 'w:bz2')

			out.add(infile, arcname=os.path.basename(infile))
			
		finally:
			if out:
				out.close()

	def get_output_filename(self, filename, additional_replacements=None):
		file = os.path.join(self.output_dir, filename)
		
		now = datetime.datetime.now()
		
		# replace all markers in the filename pattern
		file = re.compile('{YEAR}', re.IGNORECASE).sub(now.strftime('%Y'), file)
		file = re.compile('{MONTH}', re.IGNORECASE).sub(now.strftime('%m'), file)
		file = re.compile('{DAY}', re.IGNORECASE).sub(now.strftime('%d'), file)
		
		if additional_replacements:
			# additional_replacements are used f.e. in the db task
			for search, repl in additional_replacements.iteritems():
				file = re.compile(search, re.IGNORECASE).sub(repl, file)

		return file

	def create_dir_if_not_exists(self, dir):
		if not os.path.exists(dir) or not os.path.isdir(dir):
			os.mkdir(dir)

	def execute(self):
		databases = None
		
		# get a list of all databases if seperate_databases = True
		if self.seperate_databases:
			databases = self.get_db_names()

		outfiles = []

		if databases:
			for db in databases:
				if db != "information_schema" and db != "performance_schema":
					# dump the current database
					out = self.get_output_filename(self.filename_pattern_single, { '{DATABASE}': db })
					self.create_dir_if_not_exists(os.path.dirname(out))
					outfiles.append(out)
					self.dump_database(db, out)
		else:
			# otherwise, put all databases in one big file
			out = self.get_output_filename(self.filename_pattern_all)
			self.create_dir_if_not_exists(os.path.dirname(out))
			outfiles.append(out)
			self.dump_all_databases(out)
		
		# compress the sql file if configured
		if self.compress:
			for f in outfiles:
				self.compress_file(f, f + ".tar.bz2")
				os.remove(f)

if __name__ == '__main__':
	from optparse import OptionParser

	parser = OptionParser()
	parser.add_option("-s", "--server")
	parser.add_option("-u", "--user")
	parser.add_option("-p", "--password")
	parser.add_option("-d", "--directory")

	(options, args) = parser.parse_args()

	if not options.server or not options.user or not options.password or not options.directory: 
		parser.print_help()
		sys.exit(1)
	
	dumper = DatabaseDumper(options.server, options.user, options.password, options.directory, True, True, ' '.join(args))
	dumper.execute()
