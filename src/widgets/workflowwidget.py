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
import os

from PySide import QtGui

from widgets.ui_workflowwidget import Ui_WorkflowWidget
from mountpoints.workflowstep import WorkflowStepMountPoint
from widgets.workflowgraphicsscene import WorkflowGraphicsScene
from core.workflow import WorkflowError
from tools.pmr.pmrtool import PMRTool
from tools.pmr.pmrhglogindialog import PMRHgLoginDialog
from core.threadcommandmanager import CommandCloneWorkspace, CommandIgnoreDirectoriesHg

class WorkflowWidget(QtGui.QWidget):
    '''
    classdocs
    '''
    def __init__(self, mainWindow):
        '''
        Constructor
        '''
        QtGui.QWidget.__init__(self)
        self._mainWindow = mainWindow
        self._ui = Ui_WorkflowWidget()
        self._ui.setupUi(self)

        self._undoStack = QtGui.QUndoStack(self)
        self._undoStack.indexChanged.connect(self.undoStackIndexChanged)

        self._workflowManager = self._mainWindow.model().workflowManager()
        self._graphicsScene = WorkflowGraphicsScene(self)
        self._ui.graphicsView.setScene(self._graphicsScene)

        self._ui.graphicsView.setUndoStack(self._undoStack)
        self._graphicsScene.setUndoStack(self._undoStack)

        self._graphicsScene.setWorkflowScene(self._workflowManager.scene())
        self._graphicsScene.selectionChanged.connect(self._ui.graphicsView.selectionChanged)

        self._ui.executeButton.clicked.connect(self.executeWorkflow)
        self.action_Close = None  # Keep a handle to this for modifying the Ui.
        self._createMenuItems()
        # load tools
#        self.toolPlugins = ToolMountPoint.getPlugins(self.menu_Tools, self)

        self.updateStepTree()

        self._updateUi()

    def _updateUi(self):
        wfm = self._mainWindow.model().workflowManager()
        self._mainWindow.setWindowTitle(wfm.title())
        workflowOpen = wfm.isWorkflowOpen()
        self.action_Close.setEnabled(workflowOpen)
        self.setEnabled(workflowOpen)
        self.action_Save.setEnabled(wfm.isModified())
        self._ui.executeButton.setEnabled(wfm.scene().canExecute() and not wfm.isModified())

    def updateStepTree(self):
        self._ui.stepTree.clear()
        for step in WorkflowStepMountPoint.getPlugins(''):
            self._ui.stepTree.addStep(step)

    def undoStackIndexChanged(self, index):
        self._mainWindow.model().workflowManager().undoStackIndexChanged(index)
        self._updateUi()

    def undoRedoStack(self):
        return self._undoStack

    def setActive(self):
        print('setting active - workflow widget')
        self._mainWindow.setCurrentUndoRedoStack(self._undoStack)

    def executeWorkflow(self):
        self._mainWindow.execute()  # .model().workflowManager().execute()

    def setCurrentWidget(self, widget):
        self._mainWindow.setCurrentWidget(widget)

    def setWidgetUndoRedoStack(self, stack):
        self._mainWindow.setCurrentUndoRedoStack(stack)

    def new(self, pmr=False):
        m = self._mainWindow.model().workflowManager()
        workflowDir = QtGui.QFileDialog.getExistingDirectory(self._mainWindow, caption='Select Workflow Directory', directory=m.previousLocation())
        if len(workflowDir) > 0:
            m.new(workflowDir)
            m.setPreviousLocation(workflowDir)
            if pmr:
                dir_name = os.path.basename(workflowDir)
                pmr_tool = PMRTool()
                # Get login details:
                dlg = PMRHgLoginDialog(self._mainWindow)
                if dlg.exec_():
                    repourl = pmr_tool.addWorkspace('Workflow: ' + dir_name, None)
                    c = CommandCloneWorkspace(repourl, workflowDir, dlg.username(), dlg.password())
                    c.run()
                    c = CommandIgnoreDirectoriesHg(workflowDir)
                    c.run()

            self._undoStack.clear()
            self._ui.graphicsView.setLocation(workflowDir)
            self._graphicsScene.updateModel()
            self._updateUi()
            
    def newpmr(self):
        self.new(pmr=True)

    def load(self):
        m = self._mainWindow.model().workflowManager()
        # Warning: when switching between PySide and PyQt4 the keyword argument for the directory to initialise the dialog to is different.
        # In PySide the keyword argument is 'dir'
        # In PyQt4 the keyword argument is 'directory'
        workflowDir = QtGui.QFileDialog.getExistingDirectory(self._mainWindow, caption='Open Workflow', dir=m.previousLocation(), options=QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ReadOnly)
        if len(workflowDir) > 0:
            try:
                m.load(workflowDir)
                m.setPreviousLocation(workflowDir)
                self._ui.graphicsView.setLocation(workflowDir)
                self._graphicsScene.updateModel()
                self._updateUi()
            except (ValueError, WorkflowError) as e:
                self.close()
                QtGui.QMessageBox.critical( self, 'Error Caught', 'Invalid Workflow.  ' + str(e))

    def close(self):
        m = self._mainWindow.model().workflowManager()
        self._undoStack.clear()
        m.close()
        self._graphicsScene.clear()
        self._updateUi()

    def save(self):
        m = self._mainWindow.model().workflowManager()
        m.save()
        self._updateUi()

    def _setActionProperties(self, action, name, slot, shortcut='', statustip=''):
        action.setObjectName(name)
        action.triggered.connect(slot)
        if len(shortcut) > 0:
            action.setShortcut(QtGui.QKeySequence(shortcut))
        action.setStatusTip(statustip)

    def _createMenuItems(self):
        menu_File = self._mainWindow._ui.menubar.findChild(QtGui.QMenu, 'menu_File')
        lastFileMenuAction = menu_File.actions()[-1]
        menu_New = QtGui.QMenu('&New', menu_File)            
        menu_Open = QtGui.QMenu('&Open', menu_File)

        action_NewPMR = QtGui.QAction('PMR Workflow', menu_New)
        self._setActionProperties(action_NewPMR, 'action_NewPMR', self.newpmr, 'Ctrl+N', 'Create a new PMR based Workflow')
        action_New = QtGui.QAction('Workflow', menu_New)
        self._setActionProperties(action_New, 'action_New', self.new, 'Ctrl+Shift+N', 'Create a new Workflow')
        action_OpenPMR = QtGui.QAction('PMR Workflow', menu_Open)
        self._setActionProperties(action_OpenPMR, 'action_OpenPMR', self.load, 'Ctrl+O', 'Open an existing PMR based Workflow')
        action_Open = QtGui.QAction('Workflow', menu_Open)
        self._setActionProperties(action_Open, 'action_Open', self.load, 'Ctrl+Shift+O', 'Open an existing Workflow')
        self.action_Close = QtGui.QAction('&Close', menu_File)
        self._setActionProperties(self.action_Close, 'action_Close', self.close, 'Ctrl+W', 'Close open Workflow')
        self.action_Save = QtGui.QAction('&Save', menu_File)
        self._setActionProperties(self.action_Save, 'action_Save', self.save, 'Ctrl+S', 'Save Workflow')

        menu_New.insertAction(QtGui.QAction(self), action_NewPMR)
        menu_New.insertAction(QtGui.QAction(self), action_New)
        menu_File.insertMenu(lastFileMenuAction, menu_New)
        menu_Open.insertAction(QtGui.QAction(self), action_OpenPMR)
        menu_Open.insertAction(QtGui.QAction(self), action_Open)
        menu_File.insertMenu(lastFileMenuAction, menu_Open)
        menu_File.insertSeparator(lastFileMenuAction)
        menu_File.insertAction(lastFileMenuAction, self.action_Close)
        menu_File.insertSeparator(lastFileMenuAction)
        menu_File.insertAction(lastFileMenuAction, self.action_Save)
        menu_File.insertSeparator(lastFileMenuAction)


