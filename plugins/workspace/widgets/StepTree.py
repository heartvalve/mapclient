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
from PyQt4 import QtCore, QtGui

class StepTree(QtGui.QTreeWidget):

    def __init__(self, parent=None):
        super(StepTree, self).__init__(parent)
        self.stepIconSize = 64

        size = QtCore.QSize(self.stepIconSize, self.stepIconSize)
        self.setIconSize(size)
        self.setColumnCount(1)
        self.setHeaderHidden(True)
        self.setIndentation(0)

        self.setMinimumWidth(250)

    def findParentItem(self, category):
        parentItem = None
        for index in range(self.topLevelItemCount()):
            item = self.topLevelItem(index)
            if item.text(0) == category:
                parentItem = item
                break

        return parentItem

    def addStep(self, step):

        parentItem = self.findParentItem(step.category)
        if parentItem == None:
            parentItem = QtGui.QTreeWidgetItem(self)
            parentItem.setText(0, step.category)

        if not parentItem.isExpanded():
            parentItem.setExpanded(True)

        stepItem = QtGui.QTreeWidgetItem(parentItem)
        stepItem.setText(0, step.name)
        stepItem.setIcon(0, QtGui.QIcon(step.pixmap))
        stepItem.setData(0, QtCore.Qt.UserRole, step)
        stepItem.setFlags(QtCore.Qt.ItemIsEnabled)

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if not item:
            return None

        if self.indexOfTopLevelItem(item) >= 0:
            # Item is a top level item and it doesn't have drag and drop abilities
            return QtGui.QTreeWidget.mousePressEvent(self, event)

        itemData = QtCore.QByteArray()
        dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)
        step = item.data(0, QtCore.Qt.UserRole)
        pixmap = QtGui.QPixmap(step.pixmap)
        pixmap = pixmap.scaled(64, 64, aspectRatioMode=QtCore.Qt.KeepAspectRatio, transformMode=QtCore.Qt.FastTransformation)
        hotspot = QtCore.QPoint(pixmap.width() / 2, pixmap.height() / 2)

        name = bytearray(step.name, sys.stdout.encoding)
        dataStream.writeUInt32(len(name))
        dataStream.writeRawData(name)

#        dataStream = step.serialize(dataStream)
#        dataStream << pixmap
        dataStream << hotspot

        mimeData = QtCore.QMimeData()
        mimeData.setData('image/x-workspace-step', itemData)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(hotspot)
        drag.setPixmap(pixmap)

        drag.exec_(QtCore.Qt.MoveAction)

        return QtGui.QTreeWidget.mousePressEvent(self, event)