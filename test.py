#!/usr/bin/env python
# vim: set fileencoding=utf8 shiftwidth=4 tabstop=4 textwidth=80 foldmethod=marker :
# Copyright (c) 2011, Kou Man Tong. All rights reserved.
# For licensing, see LICENSE file included in the package.

import applepushnotification.tests, sys
from os.path import realpath as r, join as j, dirname as d
from optparse import OptionParser

if __name__ == "__main__":
	parser = OptionParser(usage = \
u"""Runs applepushnotification unit test cases.
			
usage: %prog pem_file hex_token""")
	options, args = parser.parse_args()
	if len(args)< 2:
		parser.print_help()
		sys.exit(-1)

	applepushnotification.tests.pem_file = j(d(__file__), args[0])
	applepushnotification.tests.hex_token = args[1]

	applepushnotification.tests.main()
