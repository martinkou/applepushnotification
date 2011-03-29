#!/usr/bin/env python
# vim: set fileencoding=utf8 shiftwidth=4 tabstop=4 textwidth=80 foldmethod=marker :
# Copyright (c) 2010, Kou Man Tong. All rights reserved.
# For licensing, see LICENSE file included in the package.

from setuptools import setup, find_packages

setup(name = "applepushnotification",
		version="0.1.1",
		packages=["applepushnotification"],
		author = "Kou Man Tong",
		author_email = "martinkou@tixxme.com",
		description = "Apple Push Notification Service connector",
		long_description = """
An APNS connector which just works. The following items are supported:

 - Extended APNS message (most Python APNS libraries only support basic format)
 - Expiry date on notifications
 - Custom data fields
 - Unicode messages
 - Error reporting
 - Automatic feedback handling

The biggest differentiator between this connector and other libraries is that
the programmer doesn't have to manage individual APNS connections or wrappers.
This connector will reconnect to send notifications automatically, and maintain
connections opportunistically for good performance.

Depends on gevent and expects coroutine I/O style.

* This library and its author are not affiliated with Apple Inc.
        """,
		platforms = "Any",
		license = "BSD",
		keywords = "APNS push notification Apple",
        url = "https://github.com/martinkou/applepushnotification"
		)
