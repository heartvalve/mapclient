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

class ImageSourceTestCase(unittest.TestCase):


    def setUp(self):
        if os.name == 'posix' and 'DISPLAY' not in os.environ:
            self.pixmap_unavailable = True
        else:
            self.pixmap_unavailable = False

        self.my_test_app = QtGui.QApplication(sys.argv)


    def tearDown(self):
        del self.my_test_app


    def testStep(self):
        if self.pixmap_unavailable:
            return
        
        from imagesourcestep.step import ImageSourceStep
        mystep = ImageSourceStep()
        
        self.assertFalse(mystep.isConfigured())

    def testStepStatus(self):
        if self.pixmap_unavailable:
            return
        
        from imagesourcestep.widgets.configuredialog import ConfigureDialogState
        state = ConfigureDialogState()
        
        self.assertEqual(state.location(), '')
        
        newstate = ConfigureDialogState('here', 'there', True, 'anywhere', 3)
        self.assertEqual(newstate.identifier(), 'here')
        self.assertEqual(newstate.location(), 'there')
        self.assertEqual(newstate.copyTo(), True)
        self.assertEqual(newstate.imageType(), 3)
        otherstate = ConfigureDialogState('here2', '', True, 'anywhere', 3)
        self.assertEqual(otherstate.identifier(), 'here2')
        self.assertEqual(otherstate.location(), 'anywhere')
        
    if sys.version_info >= (2, 7, 0):
        @unittest.skipIf(DISABLE_GUI_TESTS, 'GUI tests are disabled')
        def testConfigure(self):
            if self.pixmap_unavailable:
                return
            
            from imagesourcestep.step import ImageSourceStep
            mystep = ImageSourceStep()
            mystep.configure()
        
    if HAVE_QTTEST:
        def testConfigureDialog(self):
            if self.pixmap_unavailable:
                return
            
            from imagesourcestep.widgets.configuredialog import ConfigureDialog, ConfigureDialogState
            state = ConfigureDialogState()
            d = ConfigureDialog(state)
            
            self.assertEqual(d._ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).isEnabled(), False)
            QTest.keyClicks(d._ui.identifierLineEdit, 'hello')
            QTest.keyClicks(d._ui.localLineEdit, 'here')
            self.assertEqual(d._ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).isEnabled(), True)
            #QTest.mouseClick(d._ui.buttonBox.button(QtGui.QDialogButtonBox.Ok), QtCore.Qt.LeftButton)
            newstate = d.getState()
            self.assertEqual(newstate.identifier(), 'hello')
            self.assertEqual(newstate.location(), 'here')
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()