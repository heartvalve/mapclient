# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/annotationdialog.ui'
#
# Created: Tue Jun 25 12:57:46 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_AnnotationDialog(object):
    def setupUi(self, AnnotationDialog):
        AnnotationDialog.setObjectName("AnnotationDialog")
        AnnotationDialog.resize(462, 560)
        self.verticalLayout_2 = QtGui.QVBoxLayout(AnnotationDialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox = QtGui.QGroupBox(AnnotationDialog)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.locationLineEdit = QtGui.QLineEdit(self.groupBox)
        self.locationLineEdit.setEnabled(False)
        self.locationLineEdit.setObjectName("locationLineEdit")
        self.horizontalLayout_2.addWidget(self.locationLineEdit)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.subjectComboBox = QtGui.QComboBox(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.subjectComboBox.sizePolicy().hasHeightForWidth())
        self.subjectComboBox.setSizePolicy(sizePolicy)
        self.subjectComboBox.setEditable(True)
        self.subjectComboBox.setObjectName("subjectComboBox")
        self.horizontalLayout.addWidget(self.subjectComboBox)
        self.predicateComboBox = QtGui.QComboBox(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.predicateComboBox.sizePolicy().hasHeightForWidth())
        self.predicateComboBox.setSizePolicy(sizePolicy)
        self.predicateComboBox.setEditable(True)
        self.predicateComboBox.setObjectName("predicateComboBox")
        self.horizontalLayout.addWidget(self.predicateComboBox)
        self.objectComboBox = QtGui.QComboBox(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.objectComboBox.sizePolicy().hasHeightForWidth())
        self.objectComboBox.setSizePolicy(sizePolicy)
        self.objectComboBox.setEditable(True)
        self.objectComboBox.setObjectName("objectComboBox")
        self.horizontalLayout.addWidget(self.objectComboBox)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.addButton = QtGui.QPushButton(self.groupBox)
        self.addButton.setObjectName("addButton")
        self.gridLayout.addWidget(self.addButton, 1, 1, 1, 1)
        self.label = QtGui.QLabel(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setMaximumSize(QtCore.QSize(0, 16777215))
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 1, 1, 1)
        self.annotationListWidget = QtGui.QListWidget(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.annotationListWidget.sizePolicy().hasHeightForWidth())
        self.annotationListWidget.setSizePolicy(sizePolicy)
        self.annotationListWidget.setObjectName("annotationListWidget")
        self.gridLayout.addWidget(self.annotationListWidget, 3, 0, 1, 1)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.removeButton = QtGui.QPushButton(self.groupBox)
        self.removeButton.setObjectName("removeButton")
        self.verticalLayout.addWidget(self.removeButton)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.verticalLayout, 3, 1, 1, 1)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(AnnotationDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(AnnotationDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), AnnotationDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), AnnotationDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AnnotationDialog)

    def retranslateUi(self, AnnotationDialog):
        AnnotationDialog.setWindowTitle(QtGui.QApplication.translate("AnnotationDialog", "Annotation Tool", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("AnnotationDialog", "Annotation Tool", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("AnnotationDialog", "Location:", None, QtGui.QApplication.UnicodeUTF8))
        self.addButton.setText(QtGui.QApplication.translate("AnnotationDialog", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("AnnotationDialog", "Annotations:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("AnnotationDialog", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.removeButton.setText(QtGui.QApplication.translate("AnnotationDialog", "Remove", None, QtGui.QApplication.UnicodeUTF8))

