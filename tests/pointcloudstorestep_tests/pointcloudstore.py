'''
Created on Feb 27, 2013

@author: hsorby
'''
import os, sys
import unittest

from PyQt4 import QtGui
try:
    from PyQt4.QtTest import QTest
    HAVE_QTTEST = True
except ImportError:
    HAVE_QTTEST = False

DISABLE_GUI_TESTS = True

class PointCloudStoreTestCase(unittest.TestCase):


    def setUp(self):
        if os.name == 'posix' and 'DISPLAY' not in os.environ:
            self.pixmap_unavailable = True
        else:
            self.pixmap_unavailable = False
            self.my_test_app = QtGui.QApplication(sys.argv)

    def tearDown(self):
        if not self.pixmap_unavailable:
            del self.my_test_app

    def testStep(self):
        if self.pixmap_unavailable:
            return
        
        from pointcloudstorestep.step import PointCloudStoreStep
        mystep = PointCloudStoreStep()
        
        self.assertFalse(mystep.isConfigured())

    def testStepStatus(self):
        from pointcloudstorestep.widgets.configuredialog import ConfigureDialogState
        state = ConfigureDialogState()
        
        self.assertEqual(state.identifier(), '')
        
        newstate = ConfigureDialogState('here')
        self.assertEqual(newstate.identifier(), 'here')
        
    if sys.version_info >= (2, 7, 0):
        @unittest.skipIf(DISABLE_GUI_TESTS, 'GUI tests are disabled')
        def testConfigure(self):
            if self.pixmap_unavailable:
                return
            
            from pointcloudstorestep.step import PointCloudStoreStep
            mystep = ImageSourceStep()
            mystep.configure()
        
    if HAVE_QTTEST:
        def testConfigureDialog(self):
            if self.pixmap_unavailable:
                return
            
            from pointcloudstorestep.widgets.configuredialog import ConfigureDialog, ConfigureDialogState
            state = ConfigureDialogState()
            d = ConfigureDialog(state)
            
            self.assertEqual(d._ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).isEnabled(), False)
            QTest.keyClicks(d._ui.identifierLineEdit, 'hello')
            self.assertEqual(d._ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).isEnabled(), True)
            #QTest.mouseClick(d._ui.buttonBox.button(QtGui.QDialogButtonBox.Ok), QtCore.Qt.LeftButton)
            newstate = d.getState()
            self.assertEqual(newstate.identifier(), 'hello')
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
