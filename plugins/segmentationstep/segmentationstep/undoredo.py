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

class CommandAdd(QtGui.QUndoCommand):
    '''
    '''
    def __init__(self, field_module, position, updateGL):
        super(CommandAdd, self).__init__()
        self._field_module = field_module
        self._position = position
        self._updateGL = updateGL
        self._id = -1
        self._node = None

    def redo(self):
        self._field_module.beginChange()
        field_cache = self._field_module.createCache()
        coordinate_field = self._field_module.findFieldByName('coordinates')
        nodeset = self._field_module.findNodesetByName('cmiss_nodes')
        template = nodeset.createNodeTemplate()
        template.defineField(coordinate_field)

        self._node = nodeset.createNode(self._id, template)
        self._id = self._node.getIdentifier()
        field_cache.setNode(self._node)
        coordinate_field.assignReal(field_cache, self._position)

        self._field_module.endChange()

        self._updateGL()

    def undo(self):
        nodeset = self._field_module.findNodesetByName('cmiss_nodes')
        nodeset.destroyNode(self._node)

        self._updateGL()
