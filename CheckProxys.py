__author__ = 'maxisoft'
__all__ = ["CheckProxys"]

import urllib2
import collections
import logging

from Proxy import Proxy, ProxyException
from threading import Thread, Lock
from thread import LockType
import Queue
import time

from utils import getPublicIp


class ProxyCheckThread(Thread):
	def __init__(self, proxy, timeout=20, group=None, target=None, name=None, args=(), kwargs={}):
		super(ProxyCheckThread, self).__init__(group, target, name, args, kwargs)
		self.proxy = proxy
		self._timeout = timeout
		self.daemon = True
		self._lock = None

	def start(self):
		assert self.lock is not None
		return super(ProxyCheckThread, self).start()

	@property
	def lock(self):
		return self._lock

	@lock.setter
	def lock(self, lock):
		assert isinstance(lock, LockType)
		self._lock = lock

	def run(self):
		super(ProxyCheckThread, self).run()
		urlo = CheckProxys.createOpenerDirector(self.proxy)
		try:
			ip = getPublicIp(urlo)
		except Exception as e:
			pass
		else:
			with self.lock:
				print(self.proxy)


class MyWorkerTimeOutThread(Thread):
	def __init__(self, worker, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
		super(MyWorkerTimeOutThread, self).__init__(group, target, name, args, kwargs, verbose)
		self.worker = worker
		self.work = True
		self.currents = dict()
		self.sub_thread_print_lock = Lock()

	def run(self):
		while self.work:
			if len(self.currents) < self.worker.chunks - 1:
				thread = self.worker.working.get()
				clock = time.clock()
				while clock in self.currents:  # should never
					time.sleep(0.001)
					clock = time.clock()
				self.currents[clock] = thread
			else:
				clock = min(self.currents.iterkeys())
				thread = self.currents[clock]
				thread.join(min(float(self.worker.timeout) / 5., 0.5))
				remove = set()
				with self.sub_thread_print_lock:
					for clock, thread in self.currents.iteritems():
						if time.clock() - clock > self.worker.timeout:
							if thread.isAlive():
								thread._Thread__stop()
							remove.add(clock)
				self.currents = {clock: thread for clock, thread in self.currents.iteritems() if not clock in remove and thread.isAlive()}


class MyWorker(object):
	def __init__(self, processes, chunk=20, timeout=15):
		super(MyWorker, self).__init__()
		if chunk < 2:
			chunk = 2
		self.processes = processes
		self.chunks = chunk
		self.timeout = timeout
		self.working = Queue.Queue(self.chunks - 1)
		self.worktthread = MyWorkerTimeOutThread(self)

	def start(self):
		self.worktthread.start()
		for process in self.processes:
			process.lock = self.worktthread.sub_thread_print_lock
			process.start()
			self.working.put(process)
		self.worktthread.work = False


class CheckProxys(object):

	def __init__(self, *args, **kwargs):
		proxys = set()

		def deep_iter_proxy(arg):
			if isinstance(arg, Proxy):
				proxys.add(arg)
			elif isinstance(arg, basestring):
				try:
					proxy = Proxy(arg)
					proxys.add(proxy)
				except ProxyException:
					pass
			elif isinstance(arg, collections.Iterable):
				for item in arg:
					deep_iter_proxy(item)

		deep_iter_proxy(args)

		processes = [ProxyCheckThread(proxy) for proxy in proxys]
		self.worker = MyWorker(processes, **kwargs)
		self.worker.start()

	@staticmethod
	def createOpenerDirector(proxy):
		proxy_support = urllib2.ProxyHandler({
			"http": "http://" + str(proxy),
			"https": "https://" + str(proxy),
		})
		return urllib2.build_opener(proxy_support)