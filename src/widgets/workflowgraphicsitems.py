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
import os, math, weakref

from PySide import QtCore, QtGui

from core.workflowscene import Connection
from tools.annotation.annotationdialog import AnnotationDialog

class ErrorItem(QtGui.QGraphicsItem):

    def __init__(self, sourceNode, destNode):
        QtGui.QGraphicsItem.__init__(self)
        self._source = weakref.ref(sourceNode)
        self._dest = weakref.ref(destNode)
        self._sourcePoint = QtCore.QPointF()
        self._destPoint = QtCore.QPointF()
        self._pixmap = QtGui.QPixmap(':/workflow/images/cancel_256.png').scaled(16, 16, aspectRatioMode=QtCore.Qt.KeepAspectRatio, transformMode=QtCore.Qt.FastTransformation)
        self._source().addArc(self)
        self._dest().addArc(self)
        self.setZValue(-1.5)
        self.adjust()
        if hasattr(sourceNode, '_step_port_items'):
            print(sourceNode._step_port_items)

    def boundingRect(self):
        extra = (16) / 2.0  # Icon size divided by two

        return QtCore.QRectF(self._sourcePoint,
                             QtCore.QSizeF(self._destPoint.x() - self._sourcePoint.x(),
                                           self._destPoint.y() - self._sourcePoint.y())).normalized().adjusted(-extra, -extra, extra, extra)

    def adjust(self):
        if not self._source() or not self._dest():
            return

        sourceCentre = self._source().boundingRect().center()
        destCentre = self._dest().boundingRect().center()
        line = QtCore.QLineF(self.mapFromItem(self._source(), sourceCentre.x(), sourceCentre.y()), self.mapFromItem(self._dest(), destCentre.x(), destCentre.y()))
        length = line.length()

        if length == 0.0:
            return

        arcOffset = QtCore.QPointF((line.dx() * 10) / length, (line.dy() * 10) / length)

        self.prepareGeometryChange()
        self._sourcePoint = line.p1() + arcOffset
        self._destPoint = line.p2() - arcOffset

    def paint(self, painter, option, widget):
        midPoint = (self._destPoint + self._sourcePoint) / 2
        # Draw the line itself.
        line = QtCore.QLineF(self._sourcePoint, self._destPoint)

        if line.length() == 0.0:
            return

        painter.setPen(QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.DashLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawLine(line)

        painter.drawPixmap(midPoint.x() - 8, midPoint.y() - 8, self._pixmap)

class Item(QtGui.QGraphicsItem):
    '''
    Class to contain the selection information that selectable scene items can be derived from.
    '''


    def __init__(self):
        QtGui.QGraphicsItem.__init__(self)

        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)

    def setSelected(self, selected):
        QtGui.QGraphicsItem.setSelected(self, selected)
        self.scene().workflowScene().setItemSelected(self.metaItem(), selected)


class Arc(Item):
    Pi = math.pi
    TwoPi = 2.0 * Pi

    Type = QtGui.QGraphicsItem.UserType + 2

    def __init__(self, sourceNode, destNode):
        Item.__init__(self)

        self._arrowSize = 10.0

        self._connection = Connection(sourceNode.parentItem()._metastep, destNode.parentItem()._metastep)

        self._sourcePoint = QtCore.QPointF()
        self._destPoint = QtCore.QPointF()
#        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self._source = weakref.ref(sourceNode)
        self._dest = weakref.ref(destNode)
        self._source().addArc(self)
        self._dest().addArc(self)
        self.setZValue(-2.0)
        self.adjust()

    def connection(self):
        return self._connection

    def type(self):
        return Arc.Type

    def metaItem(self):
        return self._connection

    def sourceNode(self):
        return self._source()

    def destinationNode(self):
        return self._dest()

    def adjust(self):
        if not self._source() or not self._dest():
            return

        sourceCentre = self._source().boundingRect().center()
        destCentre = self._dest().boundingRect().center()
        line = QtCore.QLineF(self.mapFromItem(self._source(), sourceCentre.x(), sourceCentre.y()), self.mapFromItem(self._dest(), destCentre.x(), destCentre.y()))
        length = line.length()

        if length == 0.0:
            return

        arcOffset = QtCore.QPointF((line.dx() * 10) / length, (line.dy() * 10) / length)
        self.prepareGeometryChange()
        self._sourcePoint = line.p1() + arcOffset
        self._destPoint = line.p2() - arcOffset

    def boundingRect(self):
        if not self._source() or not self._dest():
            return QtCore.QRectF()

        penWidth = 1
        extra = (penWidth + self._arrowSize) / 2.0

        sceneRect = QtCore.QRectF(self._sourcePoint,
                         QtCore.QSizeF(self._destPoint.x() - self._sourcePoint.x(),
                                       self._destPoint.y() - self._sourcePoint.y())).normalized().adjusted(-extra, -extra, extra, extra)

        return sceneRect


    def paint(self, painter, option, widget):
        if not self._source() or not self._dest():
            return

        # Draw the line itself.
        line = QtCore.QLineF(self._sourcePoint, self._destPoint)

        if line.length() == 0.0:
            return

        brush = QtGui.QBrush(QtCore.Qt.black)
        if option.state & (QtGui.QStyle.State_Selected | QtGui.QStyle.State_HasFocus):  # or self.selected:
            brush = QtGui.QBrush(QtCore.Qt.red)

        painter.setBrush(brush)

        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = Arc.TwoPi - angle


        # Draw the arrows if there's enough room.
        if line.dy() * line.dy() + line.dx() * line.dx() > 200 * self._arrowSize:
            midPoint = (self._destPoint + self._sourcePoint) / 2

            destArrowP1 = midPoint + QtCore.QPointF(math.sin(angle - Arc.Pi / 3) * self._arrowSize,
                                                          math.cos(angle - Arc.Pi / 3) * self._arrowSize)
            destArrowP2 = midPoint + QtCore.QPointF(math.sin(angle - Arc.Pi + Arc.Pi / 3) * self._arrowSize,
                                                          math.cos(angle - Arc.Pi + Arc.Pi / 3) * self._arrowSize)

            painter.drawPolygon(QtGui.QPolygonF([midPoint, destArrowP1, destArrowP2]))

        painter.setPen(QtGui.QPen(brush, 1, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        # painter.setPen(QtGui.QPen(QtCore.Qt.SolidLine))
        painter.drawLine(line)

class Node(Item):
    Type = QtGui.QGraphicsItem.UserType + 1
    Size = 64

    def __init__(self, metastep):
        Item.__init__(self)

        self._metastep = metastep
        icon = self._metastep._step._icon
        if not icon:
            icon = QtGui.QImage(':/workflow/images/default_step_icon.png')
        self._pixmap = QtGui.QPixmap.fromImage(icon).scaled(self.Size, self.Size, aspectRatioMode=QtCore.Qt.KeepAspectRatio, transformMode=QtCore.Qt.FastTransformation)

        self.setToolTip(metastep._step._name)
        
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(self.DeviceCoordinateCache)
        self.setZValue(-1)

        self._contextMenu = QtGui.QMenu()
        configureAction = QtGui.QAction('Configure', self._contextMenu)
        configureAction.triggered.connect(self.configureMe)
        annotateAction = QtGui.QAction('Annotate', self._contextMenu)
        annotateAction.setEnabled(False)
        annotateAction.triggered.connect(self.annotateMe)
        self._contextMenu.addAction(configureAction)
        self._contextMenu.addAction(annotateAction)

        self._step_port_items = []
        # Collect all ports that provide or use from the step
        uses_ports = []
        provides_ports = []
        for port in self._metastep._step._ports:
            if port.hasUses():
                uses_ports.append(port)
            if port.hasProvides():
                provides_ports.append(port)
            
        port_count = len(uses_ports)
        for index, port in enumerate(uses_ports):
            triples = port.getTriplesForPred('http://physiomeproject.org/workflow/1.0/rdf-schema#uses')
            if len(triples) == 1:
                triple = triples[0]
                port_item = StepPort(port, self)
                w = port_item.width()
                h = port_item.height()
                port_item.moveBy(-3*w/4, self.Size/2 + h/3 * (4*index - 2*(port_count-1) - 1))
                port_item.setToolTip('uses: ' + triple[2])
                self._step_port_items.append(port_item)
            else:
                print('Warning: Invalid port.')
            
        port_count = len(provides_ports)
        for index, port in enumerate(provides_ports):
            triples = port.getTriplesForPred('http://physiomeproject.org/workflow/1.0/rdf-schema#provides')
            if len(triples) == 1:
                triple = triples[0]
                port_item = StepPort(port, self)
                w = port_item.width()
                h = port_item.height()
                port_item.moveBy(self.Size - w/4, self.Size/2 + h/3 * (4*index - 2*(port_count-1) - 1))
                port_item.setToolTip('provides: ' + triple[2])
                self._step_port_items.append(port_item)
            else:
                print('Warning: Invalid port.')

        self._configure_item = ConfigureIcon(self)
        self._configure_item.moveBy(40, 40)
        
        self.updateConfigureIcon()

    def updateConfigureIcon(self):

        if self._metastep._step.isConfigured():
            self._configure_item.hide()
        else:
            self._configure_item.show()


    def setPos(self, pos):
        QtGui.QGraphicsItem.setPos(self, pos)
        self.scene().workflowScene().setItemPos(self._metastep, pos)

    def type(self):
        return Node.Type

    def configureMe(self):
        self.scene().setConfigureNode(self)
        self._metastep._step.configure()
        
    def annotateMe(self):
        dlg = AnnotationDialog(self._getStepLocation())
        dlg.setModal(True)
        dlg.exec_()

    def metaItem(self):
        return self._metastep

    def boundingRect(self):
        adjust = 2.0
        return QtCore.QRectF(-adjust, -adjust,
                             self._pixmap.width() + 2 * adjust,
                             self._pixmap.height() + 2 * adjust)

    def paint(self, painter, option, widget):
            if option.state & QtGui.QStyle.State_Selected:  # or self.selected:
                painter.setBrush(QtCore.Qt.darkGray)
                painter.drawRoundedRect(self.boundingRect(), 5, 5)

#            super(Node, self).paint(painter, option, widget)
            painter.drawPixmap(0, 0, self._pixmap)
#            if not self._metastep._step.isConfigured():
#                painter.drawPixmap(40, 40, self._configure_red)

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange and self.scene():
            return self.scene().ensureItemInScene(self, value)
        elif change == QtGui.QGraphicsItem.ItemPositionHasChanged:
            for port_item in self._step_port_items:
                port_item.itemChange(change, value)
                
        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def showContextMenu(self, pos):
        has_dir = os.path.exists(self._getStepLocation())
        self._contextMenu.actions()[1].setEnabled(has_dir)
        self._contextMenu.popup(pos)
        
    def _getStepLocation(self):
        return os.path.join(self._metastep._step._location, self._metastep._step.getIdentifier())

class StepPort(QtGui.QGraphicsEllipseItem):

    Type = QtGui.QGraphicsItem.UserType + 3
    
    def __init__(self, port, parent):
        super(StepPort, self).__init__(0, 0, 11, 11, parent=parent)
        self.setBrush(QtCore.Qt.black)
        self._port = port
        self._connections = []

    def type(self):
        return StepPort.Type
    
    def width(self):
        return self.boundingRect().width()
    
    def height(self):
        return self.boundingRect().height()

    def canConnect(self, other):
        return self._port.canConnect(other._port)
        
    def _removeDeadwood(self):
        '''
        Unfortunately the weakref doesn't work correctly for c based classes.  This function 
        removes any None type references in _connections.
        '''
        prunedArcList = [ arc for arc in self._connections if arc() ]
        self._connections = prunedArcList


    def hasArcToDestination(self, node):
        self._removeDeadwood()
        for arc in self._connections:
            if arc()._dest() == node:
                return True

        return False

    def addArc(self, arc):
        self._connections.append(weakref.ref(arc))

    def removeArc(self, arc):
        self._connections = [weakarc for weakarc in self._connections if weakarc() != arc]

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionHasChanged:
            self._removeDeadwood()
            for arc in self._connections:
                arc().adjust()

        return QtGui.QGraphicsItem.itemChange(self, change, value)



class ConfigureIcon(QtGui.QGraphicsItem):


    def __init__(self, *args, **kwargs):
        super(ConfigureIcon, self).__init__(*args, **kwargs)
        self._configure_red = QtGui.QPixmap(':/workflow/images/configure_red.png').scaled(24, 24, aspectRatioMode=QtCore.Qt.KeepAspectRatio, transformMode=QtCore.Qt.FastTransformation)

    def paint(self, painter, option, widget):
        painter.drawPixmap(0, 0, self._configure_red)

    def boundingRect(self):
        return QtCore.QRectF(0, 0, 24, 24)

    def mousePressEvent(self, event):
        event.accept()

    def mouseReleaseEvent(self, event):
        if self.scene().itemAt(event.scenePos()) == self:
            self.parentItem().configureMe()


class ArrowLine(QtGui.QGraphicsLineItem):


    def __init__(self, *args, **kwargs):
        super(ArrowLine, self).__init__(*args, **kwargs)
        self._arrowSize = 10.0
        self.setZValue(-2.0)

    def boundingRect(self):

        penWidth = 1
        extra = (penWidth + self._arrowSize) / 2.0
        line = self.line()
        return QtCore.QRectF(line.p1(),
                             QtCore.QSizeF(line.p2().x() - line.p1().x(),
                                           line.p2().y() - line.p1().y())).normalized().adjusted(-extra, -extra, extra, extra)

    def paint(self, painter, option, widget):
        super(ArrowLine, self).paint(painter, option, widget)

        line = self.line()
        if line.length() == 0:
            return

        angle = math.acos(line.dx() / line.length())
#        print('angle: ', angle)
        if line.dy() >= 0:
            angle = Arc.TwoPi - angle
        # Draw the arrows if there's enough room.
        if line.dy() * line.dy() + line.dx() * line.dx() > 200 * self._arrowSize:
            midPoint = (line.p1() + line.p2()) / 2

            destArrowP1 = midPoint + QtCore.QPointF(math.sin(angle - Arc.Pi / 3) * self._arrowSize,
                                                          math.cos(angle - Arc.Pi / 3) * self._arrowSize)
            destArrowP2 = midPoint + QtCore.QPointF(math.sin(angle - Arc.Pi + Arc.Pi / 3) * self._arrowSize,
                                                          math.cos(angle - Arc.Pi + Arc.Pi / 3) * self._arrowSize)

            painter.setBrush(QtCore.Qt.black)
#        painter.drawPolygon(QtGui.QPolygonF([line.p1(), sourceArrowP1, sourceArrowP2]))
            painter.drawPolygon(QtGui.QPolygonF([midPoint, destArrowP1, destArrowP2]))


