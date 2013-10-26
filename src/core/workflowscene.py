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
from PySide import QtCore

from mountpoints.workflowstep import workflowStepFactory


class Item(object):


    def __init__(self):
        self._selected = True

    def selected(self):
        return self._selected


class MetaStep(Item):


    Type = 'Step'

    def __init__(self, step):
        Item.__init__(self)
        self._step = step
        self._pos = QtCore.QPoint(0, 0)

    def pos(self):
        return self._pos

    def getIdentifier(self):
        return self._step.getIdentifier()

class Connection(Item):


    Type = 'Connection'

    def __init__(self, source, sourceIndex, destination, destinationIndex):
        Item.__init__(self)
        self._source = source
        self._sourceIndex = sourceIndex
        self._destination = destination
        self._destinationIndex = destinationIndex

    def source(self):
        return self._source

    def sourceIndex(self):
        return self._sourceIndex

    def destination(self):
        return self._destination

    def destinationIndex(self):
        return self._destinationIndex


def _findPath(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    if not start in graph:
        return []
    for node in graph[start]:
        if node not in path:
            newpath = _findPath(graph, node, end, path)
            if newpath:
                return newpath

    return []

def _findAllPaths(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return [path]
    if not start in graph:
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            newpaths = _findAllPaths(graph, node, end, path)
            for newpath in newpaths:
                paths.append(newpath)

    return paths

def _findEndPoint(graph, seed, path=[]):
    path = path + [seed]
    if not seed in graph:
        return path
    for node in graph[seed]:
        if node not in path:
            newpath = _findEndPoint(graph, node, path)
            if newpath:
                return newpath

    return path

def _findHead(graph, seed):
    inv_graph = {}
    for k, v in graph.items():
        for entry in v:
            inv_graph[entry] = inv_graph.get(entry, [])
            inv_graph[entry].append(k)

    path = _findEndPoint(inv_graph, seed)
    if path:
        return path[-1]

    return None

def _findTail(graph, seed):
    path = _findEndPoint(graph, seed)
    if path:
        return path[-1]

    return None

class WorkflowDependencyGraph(object):


    def __init__(self, scene):
        self._scene = scene
        self._dependencyGraph = {}
        self._topologicalOrder = []
        self._graph = []
        self._head = None
        self._tail = None
        self._current = -1

    def _findAllConnectedNodes(self):
        '''
        Return a list of all the nodes that have a connection.
        '''
        nodes = []
        for item in self._scene.items():
            if item.Type == Connection.Type:
                if item.source() not in nodes:
                    nodes.append(item.source())
                if item.destination() not in nodes:
                    nodes.append(item.destination())

        return nodes

    def _nodeIsDestination(self, graph, node):
        '''
        Determine whether or not the given node features
        in a destination of another node.  Return True if
        the node is a destination, False otherwise..
        '''
        for graph_node in graph:
            if node in graph[graph_node]:
                return True

        return False

    def _findStartingSet(self, graph, nodes):
        '''
        Find the set of all nodes that are connected but are
        not destinations for any other node.
        '''
        starting_set = []
        for node in nodes:
            # Determine if node is a destination, if it is it is not a starting node
            if not self._nodeIsDestination(graph, node):
                starting_set.append(node)

        return starting_set

    def _calculateGraph(self):
        '''
        Calculate the graph for the current set of nodes and connections.
        '''
        # Calculate the helper graph
        graph = self._calculateDependencyGraph()
        # Find all connected nodes in the graph
        nodes = self._findAllConnectedNodes()
        # Find starting point set, uses helper graph
        starting_set = self._findStartingSet(graph, nodes)

        self._topologicalOrder = self._determineTopologicalOrder(graph, starting_set)

    def _determineTopologicalOrder(self, graph, starting_set):
        '''
        Determine the topological order of the graph.  Returns
        an empty list if the graph contains a loop or consists
        of independent graphs.
        '''
        # Find topological order
        temp_graph = graph.copy()
        topologicalOrder = []
        while len(starting_set) > 0:
            node = starting_set.pop()
            topologicalOrder.append(node)
            if node in temp_graph:
                for m in temp_graph[node][:]:
                    temp_graph[node].remove(m)
                    if len(temp_graph[node]) == 0:
                        del temp_graph[node]
                    if not self._nodeIsDestination(temp_graph, m):
                        starting_set.append(m)

        # If the graph is not empty we have detected a loop,
        # or independent graphs.
        if temp_graph:
            return []

        return topologicalOrder

    def _calculateDependencyGraph(self):
        self._dependencyGraph = {}
        for item in self._scene.items():
            if item.Type == Connection.Type:
                self._dependencyGraph[item.source()] = self._dependencyGraph.get(item.source(), [])
                self._dependencyGraph[item.source()].append(item.destination())

        return self._dependencyGraph

    def _calculateGraph2(self):
        '''
        Create a dependency graph based on the items in the scene.
        '''
        seed = None

        self._graph = []
        dependencyGraph = {}
        for item in self._scene.items():
            if item.Type == Connection.Type:
                dependencyGraph[item.source()] = dependencyGraph.get(item.source(), [])
                dependencyGraph[item.source()].append(item.destination())
            elif item.Type == MetaStep.Type and seed == None:
                seed = item

        if seed:
            self._head = _findHead(dependencyGraph, seed)
            self._tail = _findTail(dependencyGraph, seed)

            self._graph = _findPath(dependencyGraph, self._head, self._tail)

    def canExecute(self):
        self._calculateGraph()

        configured = [metastep for metastep in self._graph if metastep._step.isConfigured()]
        can = len(configured) == len(self._graph) and len(self._graph) >= 0
        return can and self._current == -1

    def execute(self):
        self._current += 1
        if self._current >= len(self._graph):
            self._current = -1
        else:
            dataIn = None
            if self._current > 0:
                dataIn = self._graph[self._current - 1]._step.portOutput()
            self._graph[self._current]._step.execute(dataIn)


class WorkflowScene(object):
    '''
    This is the authoratative model for the workflow scene.
    '''

    def __init__(self, manager):
        self._manager = manager
        self._items = {}
        self._dependencyGraph = WorkflowDependencyGraph(self)

    def saveState(self, ws):
        connectionMap = {}
        stepList = []
        for item in self._items:
            if item.Type == MetaStep.Type:
                stepList.append(item)
            elif item.Type == Connection.Type:
                if item.source() in connectionMap:
                    connectionMap[item.source()].append(item)
                else:
                    connectionMap[item.source()] = [item]

        location = self._manager.location()
        ws.remove('nodes')
        ws.beginGroup('nodes')
        ws.beginWriteArray('nodelist')
        nodeIndex = 0
        for metastep in stepList:
            if metastep._step.isConfigured():
                metastep._step.serialize(location)
            ws.setArrayIndex(nodeIndex)
            ws.setValue('name', metastep._step.getName())
            ws.setValue('position', metastep._pos)
            ws.setValue('selected', metastep._selected)
            identifier = metastep._step.getIdentifier()
            if not identifier:
                identifier = ''
            ws.setValue('identifier', identifier)
            ws.beginWriteArray('connections')
            connectionIndex = 0
            if metastep in connectionMap:
                for connectionItem in connectionMap[metastep]:
                    ws.setArrayIndex(connectionIndex)
                    ws.setValue('connectedFromIndex', connectionItem.sourceIndex())
                    ws.setValue('connectedTo', stepList.index(connectionItem.destination()))
                    ws.setValue('connectedToIndex', connectionItem.destinationIndex())
                    ws.setValue('selected', connectionItem.selected())
                    connectionIndex += 1
            ws.endArray()
            nodeIndex += 1
        ws.endArray()
        ws.endGroup()

    def loadState(self, ws):
        self.clear()
        location = self._manager.location()
        ws.beginGroup('nodes')
        nodeCount = ws.beginReadArray('nodelist')
        metaStepList = []
        connections = []
        for i in range(nodeCount):
            ws.setArrayIndex(i)
            name = ws.value('name')
            position = ws.value('position')
            selected = ws.value('selected', 'false') == 'true'
            identifier = ws.value('identifier')
            step = workflowStepFactory(name, location)
            step.registerIdentifierOccursCount(self.identifierOccursCount)
            step.setIdentifier(identifier)
            metastep = MetaStep(step)
            metastep._pos = position
            metastep._selected = selected
            metaStepList.append(metastep)
            self.addItem(metastep)
            # Deserialize after adding the step to the scene, this is so
            # we can validate the step identifier
            step.deserialize(location)
            arcCount = ws.beginReadArray('connections')
            for j in range(arcCount):
                ws.setArrayIndex(j)
                connectedTo = int(ws.value('connectedTo'))
                connectedToIndex = int(ws.value('connectedToIndex'))
                connectedFromIndex = int(ws.value('connectedFromIndex'))
                selected = ws.value('selected', 'false') == 'true'
                connections.append((i, connectedFromIndex, connectedTo, connectedToIndex, selected))
            ws.endArray()
        ws.endArray()
        ws.endGroup()
        for arc in connections:
            node1 = metaStepList[arc[0]]
            node2 = metaStepList[arc[2]]
            c = Connection(node1, arc[1], node2, arc[3])
            c._selected = arc[4]
            self.addItem(c)

    def manager(self):
        return self._manager

    def canExecute(self):
        return self._dependencyGraph.canExecute()

    def execute(self):
        self._dependencyGraph.execute()

    def clear(self):
        self._items.clear()

    def items(self):
        return self._items.keys()

    def addItem(self, item):
        self._items[item] = item

    def removeItem(self, item):
        if item in self._items:
            del self._items[item]

    def setItemPos(self, item, pos):
        if item in self._items:
            self._items[item]._pos = pos

    def setItemSelected(self, item, selected):
        if item in self._items:
            self._items[item]._selected = selected

    def identifierOccursCount(self, identifier):
        '''
        Return the number of times the given identifier occurs in
        all the steps present in the workflow.  The count stops at two
        and returns indicating an excess number of the given identifier.
        An empty identifier will return the value 2 also, this is used
        to signify that the identifier is invalid.
        '''
        if len(identifier) == 0:
            return 2

        identifier_occurrence_count = 0
        for key in self._items:
            item = self._items[key]
            if item.Type == MetaStep.Type and identifier == item.getIdentifier():
                identifier_occurrence_count += 1
                if identifier_occurrence_count > 1:
                    return identifier_occurrence_count

        return identifier_occurrence_count

