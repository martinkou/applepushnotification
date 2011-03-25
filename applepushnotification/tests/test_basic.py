#!/usr/bin/env python

from applepushnotification import *
from unittest import TestCase
from applepushnotification import tests
import struct, time
try:
    import json
except ImportError, e:
    import simplejson as json

class TestBasic(TestCase):
    def test_construct_service(self):
        service = NotificationService(certfile = tests.pem_file)
        service.start()
        service.stop()
        self.assertTrue(service._send_greenlet is None)
        self.assertTrue(service._error_greenlet is None)

    def test_construct_message(self):
        token = tests.hex_token.decode("hex")
        msg = NotificationMessage(token, u"Test Message", 1, u"default",
            extra = { "q" : 16 },
            identifier = 57483123)
        encoded = str(msg)
        command, identifier, expiry, tok_length = struct.unpack("!bIIH",
                encoded[0:11])
        self.assertEquals(command, 1)
        self.assertEquals(identifier, 57483123)
        self.assertTrue(expiry > time.time())
        self.assertEquals(tok_length, 32)

        data = encoded[45:]
        m = json.loads(data)
        self.assertTrue("aps" in m)
