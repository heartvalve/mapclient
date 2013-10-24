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
from shutil import copyfile
from subprocess import call

from tools.pluginwizard.skeletonstrings import CONFIGURE_DIALOG_STRING, CONFIGURE_DIALOG_LINE, CONFIGURE_DIALOG_UI, CLASS_STRING, INIT_METHOD_STRING
from tools.pluginwizard.skeletonstrings import CONFIGURE_METHOD_STRING, IDENTIFIER_METHOD_STRING, SERIALIZE_METHOD_STRING, IMPORT_STRING, PACKAGE_INIT_STRING
from tools.pluginwizard.skeletonstrings import RESOURCE_FILE_STRING, GETIDENTIFIER_DEFAULT_CONTENT_STRING, GETIDENTIFIER_IDENTIFER_CONTENT_STRING
from tools.pluginwizard.skeletonstrings import SETIDENTIFIER_DEFAULT_CONTENT_STRING, SETIDENTIFIER_IDENTIFER_CONTENT_STRING
from tools.pluginwizard.skeletonstrings import SERIALIZE_DEFAULT_CONTENT_STRING, SERIALIZE_IDENTIFIER_CONTENT_STRING
from tools.pluginwizard.skeletonstrings import DESERIALIZE_DEFAULT_CONTENT_STRING, DESERIALIZE_IDENTIFIER_CONTENT_STRING
from tools.pluginwizard.skeletonstrings import CONFIGURE_DIALOG_INIT_ADDITIONS, CONFIGURE_DIALOG_ACCEPT_METHOD, CONFIGURE_DIALOG_MAKE_CONNECTIONS_METHOD
from tools.pluginwizard.skeletonstrings import CONFIGURE_DIALOG_IDENTIFIER_VALIDATE_METHOD, CONFIGURE_DIALOG_DEFAULT_VALIDATE_METHOD

# from tools.pluginwizard.skeletonstrings import
QT_RESOURCE_FILENAME = 'resources.qrc'
PYTHON_QT_RESOURCE_FILENAME = 'resources_rc.py'
IMAGES_DIRECTORY = 'images'
CONFIG_DIALOG_FILE = 'configuredialog.py'
QT_CONFDIALOG_UI_FILENAME = 'configuredialog.ui'
PYTHON_QT_CONFDIALOG_UI_FILENAME = 'ui_configuredialog.py'

class Skeleton(object):
    '''
    This class uses the skeleton options to write the
    skeleton code to disk.
    '''

    def __init__(self, options):
        self._options = options

    def _writePackageInit(self, init_dir):
        '''
        Write the package __init__ file.  This file imports the step, sets the 
        version number and lists the author(s) name.
        '''
        init_file = os.path.join(init_dir, '__init__.py')
        f = open(init_file, 'w')
        f.write(PACKAGE_INIT_STRING.format(package_name=self._options.getPackageName(), author_name=self._options.getAuthorName()))
        f.close()

    def _generateExecuteMethod(self, uses):
        '''
        Generates the execute method string.  Returns an empty
        string if this step has no input ports.
        '''
        method_string = ''
        uses_count = len(uses)
        if uses_count > 0:
            uses_index = 0
            method_string += '\n    def execute(self, '
            while uses_index < uses_count:
                uses_index += 1
                method_string += 'dataIn{0}'.format(uses_index)
                if uses_index != uses_count:
                    method_string += ', '

            method_string += '''):
        \'\'\'
        Add your code here that will kick off the execution of the step.
        Make sure you call the _doneExecution() method when finished.  This method
        may be connected up to a button in a widget for example.
        \'\'\'
        # Put your execute step code here before calling the '_doneExecution' method.
        self._doneExecution()
    '''
        return method_string

    def _generatePortOutputMethod(self, provides):
        '''
        Generate the port output method string.  Returns the empty
        string if this step has no output ports.
        '''
        method_string = ''
        provides_count = len(provides)
        if provides_count > 0:
            provides_index = 0
            method_string += '''
    def portOutput(self):
        \'\'\'
        Add your code here that will return the appropriate objects for this step.
        The objects must be returned in the *order* they are specified in 
        the port list.
        \'\'\'
'''
            init_out_string = ''
            return_string = '        return '
            while provides_index < provides_count:
                provides_index += 1
                if provides_count > 1 and provides_index == 1:
                    return_string += '['
                return_string += 'dataOut{0}'.format(provides_index)
                init_out_string += '        dataOut{0} = None # {1}\n'.format(provides_index, provides[provides_index - 1])
                if provides_count > 1 and provides_index != provides_count:
                    return_string += ', '

            if provides_count > 1:
                return_string += ']'
            method_string += init_out_string + return_string + '\n'

        return method_string

    def _generateConfigureMethod(self):
        method_string = CONFIGURE_METHOD_STRING
        if self._options.configCount() > 0:
            method_string += '''        dlg = ConfigureDialog()
        dlg.identifierOccursCount = self._identifierOccursCount
        dlg.setConfig(self._config)
        dlg.validate()
        dlg.setModal(True)
        
        if dlg.exec_():
            self._config = dlg.getConfig()
        
        self._configured = dlg.validate()
        self._configuredObserver()
'''
        else:
            method_string += '        pass\n'

        return method_string

    def _generateImportStatements(self):
        if self._options.configCount() > 0:
            import_string = IMPORT_STRING.format(os_import='import os\n', pyside_qtcore_import='from PySide import QtCore\n')
            import_string += 'from {package_name}.configuredialog import ConfigureDialog\n'.format(package_name=self._options.getPackageName())
        else:
            import_string = IMPORT_STRING.format(os_import='', pyside_qtcore_import='')

        return import_string

    def _writeStep(self, step_dir):
        '''
        Write the step file subject to the options set in the __init__ method.
        '''
        object_name = self._options.getName().replace(' ', '')
        init_string = INIT_METHOD_STRING.format(step_object_name=object_name, step_name=self._options.getName(), step_category=self._options.getCategory())
        image_filename = self._options.getImageFile()
        if image_filename:
            (_, tail) = os.path.split(image_filename)
            icon_string = '        self._icon =  QtGui.QImage(\':/{step_package_name}/' + IMAGES_DIRECTORY + '/{image_filename}\')\n'
            init_string += icon_string.format(step_package_name=self._options.getPackageName(), image_filename=tail)
        port_index = 0
        uses = []
        provides = []
        init_string += '''        # Ports:
'''
        while port_index < self._options.portCount():
            current_port = self._options.getPort(port_index)
            init_string += '''        self.addPort(('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                      '{0}',
                      '{1}'))\n'''.format(current_port[0], current_port[1])
            if current_port[0].endswith('uses'):
                uses.append(current_port[1])
            elif current_port[0].endswith('provides'):
                provides.append(current_port[1])
            port_index += 1

        if self._options.configCount() > 0:
            init_string += '        self._config = {}\n'
            config_index = 0
            while config_index < self._options.configCount():
                config = self._options.getConfig(config_index)
                init_string += '        self._config[\'{0}\'] = \'{1}\'\n'.format(config[0], config[1])
                config_index += 1

            init_string += '\n'

        if self._options.hasIdentifierConfig():
            id_method_string = IDENTIFIER_METHOD_STRING.format(getidentifiercontent=GETIDENTIFIER_IDENTIFER_CONTENT_STRING, setidentifiercontent=SETIDENTIFIER_IDENTIFER_CONTENT_STRING)
        else:
            id_method_string = IDENTIFIER_METHOD_STRING.format(getidentifiercontent=GETIDENTIFIER_DEFAULT_CONTENT_STRING.format(step_object_name=object_name), setidentifiercontent=SETIDENTIFIER_DEFAULT_CONTENT_STRING)

#         conf.setValue('identifier', self._config['identifier'])
#         self._config['identifier'] = conf.value('identifier', '')

        if self._options.hasIdentifierConfig():
            serialize_method_string = SERIALIZE_METHOD_STRING.format(serializecontent=SERIALIZE_IDENTIFIER_CONTENT_STRING, deserializecontent=DESERIALIZE_IDENTIFIER_CONTENT_STRING)
            serialize_config_string = ''
            deserialize_config_string = ''
            config_index = 0
            while config_index < self._options.configCount():
                config = self._options.getConfig(config_index)
                serialize_config_string += '        conf.setValue(\'{0}\', self._config[\'{0}\'])'.format(config[0])
                deserialize_config_string += '        self._config[\'{0}\'] = conf.value(\'{0}\', \'{1}\')'.format(config[0], config[1])
                config_index += 1
                if config_index < self._options.configCount():
                    serialize_config_string += '\n'
                    deserialize_config_string += '\n'


            serialize_method_string = serialize_method_string.format(serializesetvalues=serialize_config_string, deserializevalues=deserialize_config_string)
        else:
            serialize_method_string = SERIALIZE_METHOD_STRING.format(serializecontent=SERIALIZE_DEFAULT_CONTENT_STRING, deserializecontent=DESERIALIZE_DEFAULT_CONTENT_STRING)

        step_file = os.path.join(step_dir, 'step.py')
        f = open(step_file, 'w')
        f.write(self._generateImportStatements())
        f.write(CLASS_STRING.format(step_object_name=object_name, step_name=self._options.getName()))
        f.write(init_string)
        f.write(self._generateExecuteMethod(uses))
        f.write(self._generatePortOutputMethod(provides))
        f.write(self._generateConfigureMethod())
        f.write(id_method_string)
        f.write(serialize_method_string)
        f.close()

    def _writeStepPackageInit(self, init_dir):
        '''
        Write the step package __init__ file.  If a resource file
        is present then load the module in here. 
        '''
        init_file = os.path.join(init_dir, '__init__.py')
        f = open(init_file, 'w')
        image_filename = self._options.getImageFile()
        if image_filename:
            (package, _) = os.path.splitext(PYTHON_QT_RESOURCE_FILENAME)
            f.write('# Import the resource file when the module is loaded,\n')
            f.write('# this enables the framework to use the step icon.\n')
            f.write('import ' + package)
        f.close()

    def _createStepIcon(self, step_dir):
        '''
        The step icon requires the creation of directories, resources
        and files if an image file has been specified.
        
        The image file in the options is assumed to exist.
        '''
        image_filename = self._options.getImageFile()
        if image_filename:
            # Create directories
            qt_dir = os.path.join(step_dir, 'qt')
            if not os.path.exists(qt_dir):
                os.mkdir(qt_dir)
            images_dir = os.path.join(qt_dir, IMAGES_DIRECTORY)
            if not os.path.exists(images_dir):
                os.mkdir(images_dir)

            (_, tail) = os.path.split(image_filename)
            # Copy image file
            copyfile(image_filename, os.path.join(images_dir, tail))

            resource_file = os.path.join(qt_dir, QT_RESOURCE_FILENAME)
            f = open(resource_file, 'w')
            f.write(RESOURCE_FILE_STRING.format(step_package_name=self._options.getPackageName(), image_filename=tail))
            f.close()

            # Generate resources file, I'm going to assume that I can find pyside-rcc
            result = call(['pyside-rcc', '-o', os.path.join(step_dir, PYTHON_QT_RESOURCE_FILENAME), os.path.join(qt_dir, QT_RESOURCE_FILENAME)])
            if result < 0:
                print('result = ' + str(-result))

    def _createConfigDialog(self, step_dir):
        '''
        The Config dialog requires the existence of the qt directory in the
        step directory.
        
        Assume the program pyside-uic is available from the shell.
        '''
        config_count = self._options.configCount()
        if config_count > 0:
            qt_dir = os.path.join(step_dir, 'qt')
            if not os.path.exists(qt_dir):
                os.mkdir(qt_dir)

            widgets_string = ''
            set_config_string = '''
    def setConfig(self, config):
        \'\'\'
        Set the current value of the configuration for the dialog.{additional_comment}
        \'\'\'{previous_identifier}
'''
            get_config_string = '''
    def getConfig(self):
        \'\'\'
        Get the current value of the configuration from the dialog.{additional_comment}
        \'\'\'{previous_identifier}
        config = {{}}
'''
            if self._options.hasIdentifierConfig():
                set_config_string = set_config_string.format(additional_comment='  Also\n        set the _previousIdentifier value so that we can check uniqueness of the\n        identifier over the whole of the workflow.', previous_identifier='\n        self._previousIdentifier = config[\'identifier\']')
                get_config_string = get_config_string.format(additional_comment='  Also\n        set the _previousIdentifier value so that we can check uniqueness of the\n        identifier over the whole of the workflow.', previous_identifier='\n        self._previousIdentifier = self._ui.lineEdit0.text()')
            else:
                set_config_string = set_config_string.format(additional_comment='', previous_identifier='')
                get_config_string = get_config_string.format(additional_comment='', previous_identifier='')

            row_index = 0
            while row_index < self._options.configCount():
                label = self._options.getConfig(row_index)[0]
                widgets_string += CONFIGURE_DIALOG_LINE.format(row=row_index, label=label + ':  ')
                config = self._options.getConfig(row_index)
                set_config_string += '        self._ui.lineEdit{0}.setText(config[\'{1}\'])\n'.format(row_index, config[0])
                get_config_string += '        config[\'{1}\'] = self._ui.lineEdit{0}.text()\n'.format(row_index, config[0])
                row_index += 1

            set_config_string += '\n'
            get_config_string += '        return config\n'

            ui_file = os.path.join(qt_dir, QT_CONFDIALOG_UI_FILENAME)
            fui = open(ui_file, 'w')
            fui.write(CONFIGURE_DIALOG_UI.format(widgets_string))
            fui.close()

            # Difficulties arise when cross Python version calling pyside-uic.
            result = call(['pyside-uic', '-o', os.path.join(step_dir, PYTHON_QT_CONFDIALOG_UI_FILENAME), ui_file])
            if result < 0:
                result = call(['py2side-uic', '-o', os.path.join(step_dir, PYTHON_QT_CONFDIALOG_UI_FILENAME), ui_file])
                if result < 0:
                    result = call(['py3side-uic', '-o', os.path.join(step_dir, PYTHON_QT_CONFDIALOG_UI_FILENAME), ui_file])

            if result < 0:
                raise Exception('Failed to generate Python ui file using pyside-uic.')

            dialog_file = os.path.join(step_dir, CONFIG_DIALOG_FILE)
            f = open(dialog_file, 'w')
            f.write(CONFIGURE_DIALOG_STRING.format(package_name=self._options.getPackageName()))
            if self._options.hasIdentifierConfig():
                f.write(CONFIGURE_DIALOG_INIT_ADDITIONS)
                f.write(CONFIGURE_DIALOG_MAKE_CONNECTIONS_METHOD)
                f.write(CONFIGURE_DIALOG_ACCEPT_METHOD)
                f.write(CONFIGURE_DIALOG_IDENTIFIER_VALIDATE_METHOD)
            else:
                f.write(CONFIGURE_DIALOG_DEFAULT_VALIDATE_METHOD)
            f.write(get_config_string)
            f.write(set_config_string)
            f.close()

    def write(self):
        '''
        Write out the step using the options set on initialisation, assumes the output
        directory is writable otherwise an exception will be raised.
        '''
        # Make package directory
        package_dir = os.path.join(self._options.getOutputDirectory(), self._options.getPackageName())
        os.mkdir(package_dir)

        # Write the package init file
        self._writePackageInit(package_dir)

        # Make step pakcage directory
        step_package_dir = os.path.join(package_dir, self._options.getPackageName())
        os.mkdir(step_package_dir)

        # Write step packate init file
        self._writeStepPackageInit(step_package_dir)

        # Write out the step file
        self._writeStep(step_package_dir)

        # Prepare step icon
        self._createStepIcon(step_package_dir)

        # Prepare config dialog
        self._createConfigDialog(step_package_dir)


DEFAULT_AUTHOR_NAME = 'Xxxx Yyyyy'
DEFAULT_CATEGORY = 'General'

class SkeletonOptions(object):
    '''
    This class hold all the options for the skeleton plugin code.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self._name = ''
        self._packageName = ''
        self._imageFile = ''
        self._outputDirectory = ''
        self._ports = []
        self._configs = []
        self._identifierConfig = False
        self._category = DEFAULT_CATEGORY
        self._authorName = DEFAULT_AUTHOR_NAME

    def getName(self):
        return self._name

    def setName(self, name):
        self._name = name

    def getPackageName(self):
        return self._packageName

    def setPackageName(self, packageName):
        self._packageName = packageName

    def getImageFile(self):
        return self._imageFile

    def setImageFile(self, imageFile):
        self._imageFile = imageFile

    def getOutputDirectory(self):
        return self._outputDirectory

    def setOutputDirectory(self, outputDirectory):
        self._outputDirectory = outputDirectory

    def portCount(self):
        return len(self._ports)

    def getPort(self, index):
        return self._ports[index]

    def addPort(self, predicate, port_object):
        self._ports.append([predicate, port_object])

    def configCount(self):
        return len(self._configs)

    def getConfig(self, index):
        return self._configs[index]

    def addConfig(self, label, value):
        if label == 'identifier':
            self._identifierConfig = True
        self._configs.append([label, value])

    def hasIdentifierConfig(self):
        return self._identifierConfig

    def getAuthorName(self):
        return self._authorName

    def setAuthorName(self, authorName):
        if not authorName:
            authorName = DEFAULT_AUTHOR_NAME

        self._authorName = authorName

    def getCategory(self):
        return self._category

    def setCategory(self, category):
        if not category:
            category = DEFAULT_CATEGORY

        self._category = category


