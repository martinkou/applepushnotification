#!/usr/bin/env python

import ssl, gevent, time, struct
from gevent.queue import Queue
from gevent.socket import *

try:
	import json
except ImportError, e:
	import simplejson as json

class NotificationMessage(object):
	"""
	Inititalizes a push notification message.

	token - device token
	alert - message string or message dictionary
	badge - badge number
	sound - name of sound to play
	identifier - message identifier
	expiry - expiry date of message
	extra - dictionary of extra parameters
	"""
	def __init__(self, token, alert, badge = None, sound = None, identifier = 0,
			expiry = long(time.time()) + 365 * 86400, extra = None):
		if len(token) != 32:
			raise ValueError, u"Token must be a 32-byte binary string."
		if not isinstance(alert, (str, unicode, dict)):
			raise ValueError, u"Alert message must be a string or a dictionary."

		self.token = token
		self.alert = alert
		self.badge = badge
		self.sound = sound
		self.identifier = identifier
		self.expiry = expiry
		self.extra = extra

	def __str__(self):
		aps = { "alert" : self.alert }
		if self.badge is not None:
			aps["badge"] = self.badge
		if self.sound is not None:
			aps["sound"] = self.sound

		data = { "aps" : aps }
		if self.extra is not None:
			data.update(self.extra)

		encoded = json.dumps(data)
		length = len(encoded)

		return struct.pack("!bIIH32sH%(length)ds" % { "length" : length },
			1, self.identifier, self.expiry,
			32, self.token, length, encoded)

class NotificationService(object):
	def __init__(self, sandbox = True, **kwargs):
		if "certfile" not in kwargs:
			raise ValueError, u"Must specify a PEM bundle."
		self._sslargs = kwargs
		self._push_connection = None
		self._feedback_connection = None
		self._sandbox = sandbox
		self._send_queue = Queue()
		self._error_queue = Queue()
		self._feedback_queue = Queue()
		self._send_greenlet = None
		self._error_greenlet = None
		self._feedback_greenlet = None

	def _check_send_connection(self):
		if self._push_connection is None:
			s = ssl.wrap_socket(socket(AF_INET, SOCK_STREAM, 0),
				ssl_version=ssl.PROTOCOL_SSLv3,
				**self._sslargs)
			addr = ("gateway.push.apple.com", 2195)
			if self._sandbox:
				addr[0] = "gateway.sandbox.push.apple.com"
			s.connect(addr)
			self._push_connection = s
			gevent.spawn(self._error_loop)

	def _check_feedback_connection(self):
		if self._feedback_connection is None:
			s = ssl.wrap_socket(socket(AF_INET, SOCK_STREAM, 0),
				ssl_version = ssl.PROTOCOL_SSLv3,
				**self._sslargs)
			addr = ("feedback.push.apple.com", 2196)
			if self._sandbox:
				addr[0] = "feedback.sandbox.push.apple.com"
			s.connect(addr)
			self._feedback_connection = s

	def _send_loop(self):
		self._send_greenlet = gevent.getcurrent()
		try:
			while True:
				msg = self._send_queue.get()
				self._check_send_connection()
				try:
					self._push_connection.send(str(msg))
				except:
					self._send_queue.put(msg)
					gevent.sleep(5.0)
		except gevent.GreenletExit, e:
			pass
		finally:
			self._send_greenlet = None

	def _error_loop(self):
		self._error_greenlet = gevent.getcurrent()
		try:
			while True:
				msg = self._push_connection.recv(1 + 1 + 4)
				if len(msg) < 6:
					return
				data = struct.unpack("!bbI", msg)
				self._error_queue.put((data[1], data[2]))
		except gevent.GreenletExit, e:
			pass
		finally:
			self._push_connection.close()
			self._push_connection = None
			self._error_greenlet = None

	def _feedback_loop(self):
		self._feedback_greenlet = gevent.getcurrent()
		try:
			self._check_feedback_connection()
			while True:
				msg = self._feedback_connection.recv(4 + 2 + 32)
				if len(msg) < 38:
					return
				data = struct.unpack("!IH32s", msg)
				self._feedback_queue.put((data[0], data[2]))
		except gevent.GreenletExit, e:
			pass
		finally:
			self._feedback_connection.close()
			self._feedback_connection = None
			self._feedback_greenlet = None

	def send(self, obj):
		"""Send a push notification"""
		if not isinstance(obj, NotificationMessage):
			raise ValueError, u"You can only send NotificationMessage objects."
		self._send_queue.put(obj)

	def get_error(self, block = True, timeout = None):
		"""Gets the next error message.
		
		Each error message is a 2-tuple of (status, identifier)."""
		return self._error_queue.get(block = block, timeout = timeout)

	def get_feedback(self, block = True, timeout = None):
		"""Gets the next feedback message.

		Each feedback message is a 2-tuple of (timestamp, device_token)."""
		return self._feedback_queue.get(block = block, timeout = timeout)

	def start(self):
		"""Start the message sending loop."""
		if self._send_greenlet is None:
			gevent.spawn(self._send_loop)

	def stop(self):
		"""Stop sending messages, close connection."""
		if self._send_greenlet is not None:
			gevent.kill(self._send_greenlet)
		if self._error_greenlet is not None:
			gevent.kill(self._error_greenlet)
