'''
MAP Client, a program to generate detailed musculoskeletal models for OpenSim.
    Copyright (C) 2012  University of Auckland

This file is part of MAP Client. (http://launchpad.net/mapclient)

    MAP Client is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    MAP Client is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with MAP Client.  If not, see <http://www.gnu.org/licenses/>..
'''
import sys

if sys.version_info < (2, 7):
    try:
        from unittest2 import TestCase, main, skipUnless
    except ImportError:
        print('Go install unittest2 in python2.6, all tests are skipped.')
        main = TestCase = object
        def skipUnless(cond, reason):
            def decorator(obj):
                return obj
            return decorator
else:
    from unittest import TestCase, main, skipUnless


REQUESTS_TESTADAPTER = True
try:
    from requests_testadapter import TestAdapter, TestSession
except:
    print('Missing `requests_testadapter`; all requests tests are skipped')
    REQUESTS_TESTADAPTER = False

import json
import tempfile
import os
import shutil

from PySide.QtCore import QSettings

from mapclient.tools.pmr.pmrtool import PMRTool
from mapclient.settings.info import PMRInfo

workspace_home = json.dumps({
    u'workspace-home': {
        u'target': u'http://example.com/dashboard/home',
        u'label': u'Workspace home'
    },
    u'workspace-add': {
        u'target': u'http://example.com/dashboard/addWorkspace',
        u'label': u'Create workspace in workspace home',
    },
})


@skipUnless(REQUESTS_TESTADAPTER, 'No need to create workspaces all the time.')
class PMRToolTestCase(TestCase):

    test_level = 1

    def setUp(self):
        self.working_dir = tempfile.mkdtemp()

        # Because uh, QSettings has very nice API so we need this
        QSettings.setDefaultFormat(QSettings.Format.IniFormat)

        # and this line, which include
        QSettings.setPath(
            QSettings.Format.IniFormat,  # this arg
            QSettings.Scope.SystemScope,
            self.working_dir,
        )

        # to have our test settings isolated from the real application.
        # Insert profanity here: ________________

        # now we make our info
        info = PMRInfo()

        self.endpoints = [
            (info.host + '/pmr2-dashboard',
                TestAdapter(stream=workspace_home)),

            ('http://example.com/dashboard/addworkspace',
                TestAdapter(
                    stream='',
                    headers={
                        'Location': 'http://example.com/w/+/addworkspace',
                    }
                )
            ),

            ('http://example.com/w/+/addworkspace',
                TestAdapter(
                    # XXX need to make this a real thing when we test that
                    # responses from server matters.
                    stream='',
                    headers={
                        'Location': 'http://example.com/w/1',
                    }
                )
            ),

            ('http://example.com/w/1',
                TestAdapter(
                    # XXX need to make this a real thing when we test that
                    # responses from server matters.
                    stream='{"url": "http://example.com/w/1"}',
                )
            ),

        ]

        # and tool, with the end points.
        self._tool = self.make_tool()

    def tearDown(self):
        shutil.rmtree(self.working_dir)

    def make_tool(self):
        def make_session(pmr_info=None):
            session = TestSession()
            for url, adapter in self.endpoints:
                session.mount(url, adapter)
            return session
        tool = PMRTool()
        tool.make_session = make_session
        return tool

    def tearDown(self):
        pass

    def testAddWorkspace(self):
        info = PMRInfo()
        location = self._tool.addWorkspace('my title', 'my description')
        self.assertTrue(location.startswith('http://'))

    def testGetDashboard(self):
        info = PMRInfo()
        d = self._tool.getDashboard()
        self.assertTrue('workspace-home' in d)
        self.assertTrue('workspace-add' in d)

    def test_hasAccess(self):
        # update tokens using another instance
        info = PMRInfo()
        t = PMRTool()
        # Ensure no access
        info.update_token('', '')
        self.assertFalse(t.hasAccess())

        info.update_token('test', 'token')
        # Now it's true
        self.assertTrue(t.hasAccess())

        # revoke access again.
        info.update_token('', '')
        # Now it's false again.
        self.assertFalse(t.hasAccess())


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    main()
