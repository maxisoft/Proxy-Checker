__author__ = 'maxisoft'
__all__ = ['Proxy']

import socket
import re
from functools import total_ordering


class ProxyException(Exception):
	def __init__(self, original, *args, **kwargs):
		super(ProxyException, self).__init__(*args, **kwargs)
		self.originalexception = original


@total_ordering
class Proxy(object):
	DEFAULT_PORT = 8080

	def __init__(self, s, port=None):
		try:
			if port is None:
				port = re.search('(?<=[:,/])[0-9]*', s)
				if port is None:
					ip = s
					port = Proxy.DEFAULT_PORT
				else:
					port, start = port.group(0), port.start()
					ip = s[:start-1]
			else:
				ip = s
			ip = socket.inet_aton(ip)
			port = int(port)
			assert 0 < port < 2**16
		except Exception as e:
			raise ProxyException(e, "illegal proxy address")
		else:
			self._ip = ip
			self._port = port

	@property
	def ip(self):
		return socket.inet_ntoa(self._ip)

	@property
	def port(self):
		return self._port

	def __str__(self):
		return str(self.ip) + ':' + str(self.port)

	def __repr__(self):
		return "<%s>(%s)" % (self.__class__.__name__, self.__str__())

	def __hash__(self):
		return hash(self._ip + str(self._port))

	def __eq__(self, other):
		return self._ip == other._ip and self._port == other._port

	def __lt__(self, other):
		if self._ip < other._ip:
			return True
		if self._ip > other._ip:
			return False
		if self._port < other._port:
			return True
		if self._port > other._port:
			return False
		return False