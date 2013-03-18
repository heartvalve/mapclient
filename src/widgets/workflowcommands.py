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
from PyQt4 import QtGui

from widgets.workflowgraphicsitems import Node

class CommandRemove(QtGui.QUndoCommand):
    '''
    '''
    def __init__(self, scene, selection):
        super(CommandRemove, self).__init__()
        self._scene = scene
        self._items = []
        for item in selection:
            if item not in self._items:
                self._items.append(item)
            if item.Type == Node.Type:
                for edge in item._connections:
                    if edge() not in self._items:
                        self._items.append(edge())

    def redo(self):
        self._scene.blockSignals(True)
        for item in self._items:
            self._scene.removeItem(item)
        self._scene.blockSignals(False)

    def undo(self):
        self._scene.blockSignals(True)
        for item in self._items:
            self._scene.addItem(item)
        self._scene.blockSignals(False)


class CommandSelection(QtGui.QUndoCommand):
    '''
    We block signals  when setting the selection so that we
    don't end up in a recursive loop.
    '''
    def __init__(self, scene, selection, previous):
        super(CommandSelection, self).__init__()
        self._scene = scene
        self._selection = selection
        self._previousSelection = previous

    def redo(self):
        self._scene.blockSignals(True)
        for item in self._scene.items():
            item.setSelected(item in self._selection)
        self._scene.blockSignals(False)

    def undo(self):
        self._scene.blockSignals(True)
        for item in self._scene.items():
            item.setSelected(item in self._previousSelection)
        self._scene.blockSignals(False)


class CommandAdd(QtGui.QUndoCommand):
    '''
    '''
    def __init__(self, scene, item):
        super(CommandAdd, self).__init__()
        self._scene = scene
        self.item = item

    def undo(self):
        self._scene.blockSignals(True)
        self._scene.removeItem(self.item)
        self._scene.blockSignals(False)

    def redo(self):
        self._scene.blockSignals(True)
        self._scene.addItem(self.item)
        self._scene.blockSignals(False)


class CommandMove(QtGui.QUndoCommand):
    '''
    '''
    def __init__(self, node, posFrom, posTo):
        super(CommandMove, self).__init__()
        self._node = node
        self._from = posFrom
        self._to = posTo

    def redo(self):
        self._node.setPos(self._to)

    def undo(self):
        self._node.setPos(self._from)


class CommandConfigure(QtGui.QUndoCommand):
    

    def __init__(self, scene):
        super(CommandConfigure, self).__init__()
        self._scene = scene
        
    def redo(self):
        for item in self._scene.items():
            item.update()

    def undo(self):
        for item in self._scene.items():
            item.update()

