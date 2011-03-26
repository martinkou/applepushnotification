#!/usr/bin/env python

import os
import sys
import unittest
import doctest
from random import randint

here = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from applepushnotification import *

# The following vars are set by test.py at launch
pem_file = None
hex_token = None

class TestAPNS(unittest.TestCase):
    def create_message(self, text = None):
        global hex_token, pem_file
        token = hex_token.decode("hex")
        if text is None:
            text = u"Test Message %d" % (randint(10000, 99999),)
        msg = NotificationMessage(token, text, randint(1, 10),
            u"default", extra = { "q" : randint(10000, 99999) },
            identifier = randint(10000000, 99999999))
        return msg

    def create_service(self):
        global hex_token, pem_file
        service = NotificationService(certfile = pem_file)
        return service

def test_suite():
    suite = additional_tests()
    loader = unittest.TestLoader()
    for fn in os.listdir(here):
        if fn.startswith("test") and fn.endswith(".py"):
            modname = "applepushnotification.tests." + fn[:-3]
            __import__(modname)
            module = sys.modules[modname]
            suite.addTests(loader.loadTestsFromModule(module))
    return suite

def additional_tests():
    import bson 
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(bson))
    return suite

def main():
    suite = test_suite()
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == '__main__':
    main()
