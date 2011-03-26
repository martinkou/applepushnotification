#!/usr/bin/env python

from applepushnotification import *
from unittest import TestCase
from applepushnotification.tests import TestAPNS
import struct, time, sys

class TestDisconnect(TestAPNS):
    def test_disconnect(self):
        service = self.create_service()
        service.send(self.create_message())
        service.start()
        service.wait_send(10.0)
        self.assertTrue(service._push_connection is not None)
        service._push_connection.close()
        service.send(self.create_message())
        self.assertTrue(service._send_greenlet is not None)
        retval = service.stop()
