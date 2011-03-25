#!/usr/bin/env python

from applepushnotification import *
from unittest import TestCase
from applepushnotification.tests import TestAPNS
import struct, time
try:
    import json
except ImportError, e:
    import simplejson as json

class TestBasic(TestAPNS):
    def test_construct_service(self):
        service = self.create_service()
        service.start()
        service.stop()
        self.assertTrue(service._send_greenlet is None)
        self.assertTrue(service._error_greenlet is None)

    def test_construct_message(self):
        msg = self.create_message()
        encoded = str(msg)
        command, identifier, expiry, tok_length = struct.unpack("!bIIH",
                encoded[0:11])
        self.assertEquals(command, 1)
        self.assertEquals(identifier, msg.identifier)
        self.assertTrue(expiry > time.time())
        self.assertEquals(tok_length, 32)

        data = encoded[45:]
        m = json.loads(data)
        self.assertTrue("aps" in m)

    def test_send_message(self):
        service = self.create_service()
        service.start()
        service.send(self.create_message())
        self.assertTrue(service.stop())
