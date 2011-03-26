#!/usr/bin/env python

from applepushnotification import *
from unittest import TestCase
from applepushnotification.tests import TestAPNS
import os

class TestError(TestAPNS):
    def test_error(self):
        service = self.create_service()
        msg = self.create_message()
        msg.token = os.urandom(32)
        service.start()
        service.send(msg)
        err_status, err_identifier = service.get_error(timeout = 10.0)
        self.assertEquals(err_identifier, msg.identifier)
        self.assertEquals(err_status, 8)
        self.assertTrue(service.stop())
