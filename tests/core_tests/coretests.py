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
import unittest

def suite():
    tests = unittest.TestSuite()
    
    from core_tests.pluginframework import PluginFrameworkTestCase
    tests.addTests(unittest.TestLoader().loadTestsFromTestCase(PluginFrameworkTestCase))
    
    from core_tests.mainapplication import MainApplicationTestCase
    tests.addTests(unittest.TestLoader().loadTestsFromTestCase(MainApplicationTestCase))

    from core_tests.workflowscene import WorkflowSceneTestCase, WorkflowDependencyGraphTestCase, GraphUtilitiesTestCase
    tests.addTests(unittest.TestLoader().loadTestsFromTestCase(WorkflowSceneTestCase))
    tests.addTests(unittest.TestLoader().loadTestsFromTestCase(WorkflowDependencyGraphTestCase))
    tests.addTests(unittest.TestLoader().loadTestsFromTestCase(GraphUtilitiesTestCase))

    from core_tests.threadcommandmanager import ThreadCommandManagerTestCase
    tests.addTests(unittest.TestLoader().loadTestsFromTestCase(ThreadCommandManagerTestCase))

    return tests

def load_tests(loader, tests, pattern):
    return suite()

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())