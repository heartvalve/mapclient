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
import os, tempfile
from threading import Thread
from os import listdir
from os.path import isfile, join, isdir
from shutil import copy, move, rmtree
from subprocess import call#, Popen

class ThreadCommand(Thread):
    '''Base class for threaded commands to be used by the CommandThreadManager.
    Set the _caller for a callback to the manager to inform the manager that
    the thread has finished.  Also call runFinished when at the end of the run method
    in any derived classes.
    '''
    _caller = None


    def __init__(self, name=None):
        '''
        Constructor, setting the name for printing out readable text.
        It has no functional purpose.
        '''
        Thread.__init__(self, name=name)
        
    def setCaller(self, caller):
        self._caller = caller
        
    def runFinished(self):
        self._caller and self._caller._commandFinished(self.name)
    
    
class CommandCopyDirectory(ThreadCommand):
    ''' Threadable command to copy the contents of one directory to another.
    This copy is not recursive.
    '''
    
    def __init__(self, from_dir, to_dir):
        ThreadCommand.__init__(self, 'CommandCopyDirectory')
        self._from_dir = from_dir
        self._to_dir = to_dir
        
    def run(self):
        onlyfiles = [ join(self._from_dir, f) for f in listdir(self._from_dir) if isfile(join(self._from_dir, f)) ]
        for f in onlyfiles:
            copy(f, self._to_dir)
            
        self.runFinished()
        
        
class CommandCreateWorkspace(ThreadCommand):
    '''Threadable command to create a workspace on PMR.
    '''
    def __init__(self, title, description=None):
        ThreadCommand.__init__(self, 'CommandCreateWorkspace')
        self._title = title
        self._description = description
        
    def run(self):
        print('Warning: Not fully implemented')
        self.runFinished()
        
    
class CommandIgnoreDirectoriesHg(ThreadCommand):
    ''' Threadable command to add ignore directives to
    all directories in given location.  Requires a Mercurial
    repository to be already present in the given location.
    '''
    def __init__(self, location):
        ThreadCommand.__init__(self, 'CommandIgnoreDirectoriesHg')
        self._location = location
        self._hg = None
        hg = which('hg')
        if len(hg) > 0:
            self._hg = hg[0] 
        
    def run(self):
        if self._hg and os.path.exists(join(self._location, '.hg')):
            onlydirs = [x for x in listdir(self._location) if isdir(join(self._location, x)) ]
            ignoredirs = ['^' + d + '/.*\n' for d in onlydirs if d != '.hg']
            f = open(join(self._location, '.hgignore'), 'w')
            f.writelines(ignoredirs)
            f.close()
    
class CommandCloneWorkspace(ThreadCommand):
    ''' Threadable command to clone a PMR workspace.
    '''
    
    def __init__(self, repourl, location, username, password):
        ThreadCommand.__init__(self, 'CommandCloneWorkspace')
        self._repourl = repourl
        self._location = location
        self._username = username
        self._password = password
        self._hg = None
        hg = which('hg')
        if len(hg) > 0:
            self._hg = hg[0] 
        
    def run(self):
        '''Mercurial will not clone into a directory that is not empty.  To work
        around this we clone into a temporary directory and then move the '.hg'
        directory structure into the desired directory.
        '''
        if self._hg and not os.path.exists(join(self._location, '.hg')):
            d = tempfile.mkdtemp(dir=self._location)
            
            repourl = self._repourl[:7] + self._username + ':' + self._password + '@' + self._repourl[7:]
            call([self._hg, 'clone', repourl, d])
            move(join(d, '.hg'), self._location)
            rmtree(d)
# This is for the commit command
#                call([self._hg, 'add', self._location])
#                message = 'Initial commit of directory contents.'
#                process = Popen([self._hg, 'commit', '-u', u, '-m', message], cwd=self._location)
#                process.communicate()
#                process = Popen([self._hg, 'push', repourl], cwd=self._location)
#                process.communicate()
                
        
        print('call complete')
        self.runFinished()
    
class ThreadCommandManager(object):
    '''This class managers thread commands in a queue.  The queue will
    be executed in order serially.
    '''
    
    def __init__(self):
        self._queue = []
        self._finished = None # Callback for informing when the queue is empty
        
    def registerFinishedCallback(self, callback):
        self._finished = callback
        
    def addCommand(self, c):
        self._queue.append(c)
        
    def execute(self):
        if len(self._queue) > 0:
            c = self._queue.pop(0)
            c.setCaller(self)
            c.start()
        elif self._finished:
            self._finished()
        
    def _commandFinished(self, thread_name):
        self.execute()
        

def which(name, flags=os.X_OK):
        result = []
        exts = filter(None, os.environ.get('PATHEXT', '').split(os.pathsep))
        path = os.environ.get('PATH', None)
        if path is None:
            return []
        for p in os.environ.get('PATH', '').split(os.pathsep):
            p = os.path.join(p, name)
            if os.access(p, flags):
                result.append(p)
            for e in exts:
                pext = p + e
                if os.access(pext, flags):
                    result.append(pext)
        return result
    