__author__ = 'maxisoft'

import sys
import urllib2
from CheckProxys import CheckProxys
from utils import get_all_proxy

from optparse import OptionParser, OptionGroup


def main():
	proxys = ""
	usage = "usage: %prog [options] [proxys...]"
	parser = OptionParser(usage)

	group = OptionGroup(parser, "Advanced Options")
	group.add_option("-n", "--nbr_proxy_check", dest="chunk", help="max number of simultaneous proxys checks", default=20, type="int")
	group.add_option("-t", "--timeout", dest="timeout", help="proxy TIMEOUT", default=15, type="int")
	group.add_option("-a", "--append", action="store_true", dest="append", help="append to report file", default=False)
	parser.add_option_group(group)

	parser.add_option("-f", "--file", dest="infilename", help="read proxys from FILE", metavar="FILE")
	parser.add_option("-u", "--url", dest="url", help="read proxys from URL")
	parser.add_option("-w", "-o", "--write", dest="outfilename", help="write report to FILE", metavar="FILE", default=None)

	(options, args) = parser.parse_args()

	if args:
		proxys += " ".join(args)
	elif not options.infilename and not options.url:
		sys.stderr.write("Invalid usage.")
		exit(10)

	if options.timeout < 1:
		sys.stderr.write("Invalid usage, timeout arg must be positive")
		exit(11)

	if options.chunk < 1:
		sys.stderr.write("Invalid usage, chunk arg must be positive")
		exit(12)

	if options.infilename:
		with open(options.infilename) as f:
			proxys += f.read()

	if options.url:
		proxys += urllib2.urlopen(options.url).read()

	if options.outfilename:
		mode = "a" if options.append else "w"
		sys.stdout = open(options.outfilename, mode)

	proxys = get_all_proxy(proxys)

	if not proxys:
		sys.stderr.write("There's no proxy :(")
		exit(13)
	CheckProxys(proxys, timeout=options.timeout, chunk=options.chunk)


if __name__ == '__main__':
	main()
