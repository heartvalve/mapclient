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

from core import pluginframework

class WorkspaceStepPort(object):
    '''
    Describes the location and properties of a port for a workspace step.
    '''
    def __init__(self):
        self.subj = {}
        self.pred = {}
        self.obj = {}

    def addProperty(self, rdftriple):
        if rdftriple[0] in self.subj:
            self.subj[rdftriple[0]].append(rdftriple)
        else:
            self.subj[rdftriple[0]] = [rdftriple]

        if rdftriple[1] in self.pred:
            self.pred[rdftriple[1]].append(rdftriple)
        else:
            self.pred[rdftriple[1]] = [rdftriple]

        if rdftriple[2] in self.obj:
            self.obj[rdftriple[2]].append(rdftriple)
        else:
            self.obj[rdftriple[2]] = [rdftriple]

    def getTriplesForObj(self, obj):
        if obj in self.obj:
            return self.obj[obj]

        return []
#        return [triple[2] for triple in self.obj[obj]]

    def getTriplesForPred(self, pred):
        if pred in self.pred:
            return self.pred[pred]

        return []
#        return [triple for triple in self.pred[pred]]

    def canConnect(self, other):
        if 'pho#workspace#port' in self.subj and 'pho#workspace#port' in other.subj:
            myPorts = self.subj['pho#workspace#port']
            thierPorts = other.subj['pho#workspace#port']
            mineProvides = [triple for triple in myPorts if 'provides' == triple[1]]
            thiersUses = [triple for triple in thierPorts if 'uses' == triple[1]]
            for mine in mineProvides:
                for thiers in thiersUses:
                    if mine[2] == thiers[2]:
                        return True

        return False

'''
Plugins can inherit this mount point to add a workspace step.

 A plugin that registers this mount point must have attributes
 * pixmap
 * name
 
 A plugin that registers this mount point could have attributes
 * category
 
 It must implement
 * serialize
 * deserialize 

'''
#class WorkspaceStep(WorkspaceStepMountPoint):
#    '''
#    A step that acts like the step plugin duck
#    '''
#
def _workspace_step_init(self):
    '''
    Constructor
    '''
    self.name = 'empty'
    self.ports = []
    self.pixmap = None
    self.configured = False

def _workspace_step_configure(self):
    raise NotImplementedError

def _workspace_step_isConfigured(self):
    return self.configured

def _workspace_step_addPort(self, triple):
    port = WorkspaceStepPort()
    port.addProperty(triple)
    self.ports.append(port)

def _workspace_step_canConnect(self, other):
    # Try to find compatible ports
    for port in self.ports:
        for otherPort in other.ports:
            if port.canConnect(otherPort):
                return True

    return False

attr_dict = {'category': 'General'}
attr_dict['__init__'] = _workspace_step_init
attr_dict['configure'] = _workspace_step_configure
attr_dict['isConfigured'] = _workspace_step_isConfigured
attr_dict['addPort'] = _workspace_step_addPort
attr_dict['canConnect'] = _workspace_step_canConnect


WorkspaceStepMountPoint = pluginframework.MetaPluginMountPoint('WorkspaceStepMountPoint', (object,), attr_dict)

def workspaceStepFactory(step_name):
    for step in WorkspaceStepMountPoint.getPlugins():
        if step_name == step.name:
            return step
        
    raise ValueError


