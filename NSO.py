
import sys
import os
from functools import partial
import _pickle
import json
from PyQt5 import QtGui,QtCore,QtWidgets
import sip
super_class = QtWidgets.QMainWindow

try:
    UNICODE_EXISTS = bool(type(unicode))
except NameError:
    unicode = lambda s: str(s)

class NSO(super_class):
    def __init__(self, parent=None, mode=0):
        super_class.__init__(self, parent)

        self.version="0.1"
        self.help = ""
        self.uiList={}
        self.memoData = {}
        self.location = ""
        if getattr(sys, 'frozen', False):
            self.location = sys.executable
        else:
            self.location = os.path.realpath(__file__)

        self.name = self.__class__.__name__
        self.iconPath = os.path.join(os.path.dirname(self.location),'icons',self.name+'.png')
        self.iconPix = QtGui.QPixmap(self.iconPath)
        self.icon = QtGui.QIcon(self.iconPath)
        self.fileType='.{0}_EXT'.format(self.name)

    def setupStyle(self):
        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Cleanlooks'))
        self.setStyleSheet("QLineEdit:disabled{background-color: gray;}")

    def setupMenu(self):

        if 'help_menu' in self.uiList.keys():
            cur_menu = self.uiList['help_menu']
            cur_menu.addSeparator()
            self.uiList['helpGuide_msg'] = self.help
            self.quickMenuAction('helpGuide_atnMsg','Usage Guide','How to Usge Guide.','helpGuide.png', cur_menu)
    def setupWin(self):
        self.setWindowTitle(self.name + " - v" + self.version)
        self.setWindowIcon(self.icon)
        self.drag_position=QtGui.QCursor.pos()

    def qui(self, ui_list_string, parentObject_string='', opt=''):
        type_dict = {
            'vbox': 'QVBoxLayout','hbox':'QHBoxLayout','grid':'QGridLayout', 'form':'QFormLayout',
            'split': 'QSplitter', 'grp':'QGroupBox', 'tab':'QTabWidget',
            'btn':'QPushButton', 'btnMsg':'QPushButton', 'label':'QLabel', 'input':'QLineEdit', 'check':'QCheckBox', 'choice':'QComboBox',
            'txt': 'QTextEdit',
            'list': 'QListWidget', 'tree': 'QTreeWidget', 'table': 'QTableWidget',
            'space': 'QSpacerItem',
        }
        ui_list = [x.strip() for x in ui_list_string.split('|')]
        for i in range(len(ui_list)):
            if ui_list[i] in self.uiList:
                ui_list[i] = self.uiList[ui_list[i]]
            else:
                partInfo = ui_list[i].split(';',1)
                uiName = partInfo[0].split('@')[0]
                uiType = uiName.rsplit('_',1)[-1]
                if uiType in type_dict:
                    uiType = type_dict[uiType]
                ui_list[i] = partInfo[0]+';'+uiType
                if len(partInfo)==1:
                    if uiType in ('btn', 'btnMsg', 'QPushButton','label', 'QLabel'):
                        ui_list[i] = partInfo[0]+';'+uiType + ';'+uiName
                elif len(partInfo)==2:
                    ui_list[i]=ui_list[i]+";"+partInfo[1]
        parentObject = parentObject_string
        if parentObject in self.uiList:
            parentObject = self.uiList[parentObject]
        self.quickUI(ui_list, parentObject, opt)

    def setupUI(self):
        main_layout = None
        if isinstance(self, QtWidgets.QMainWindow):
            main_widget = QtWidgets.QWidget()
            self.setCentralWidget(main_widget)
            main_layout = self.quickLayout('vbox', 'main_layout')
            main_widget.setLayout(main_layout)
        else:
            main_layout = self.quickLayout('vbox', 'main_layout')
            self.setLayout(main_layout)

    def Establish_Connections(self):
        for ui_name in self.uiList.keys():
            if ui_name.endswith('_btn'):
                self.uiList[ui_name].clicked.connect(getattr(self, ui_name[:-4]+"_action", partial(self.default_action,ui_name)))
            elif ui_name.endswith('_atn'):
                self.uiList[ui_name].triggered.connect(getattr(self, ui_name[:-4]+"_action", partial(self.default_action,ui_name)))
            elif ui_name.endswith('_btnMsg'):
                self.uiList[ui_name].clicked.connect(getattr(self, ui_name[:-7]+"_message", partial(self.default_message,ui_name)))
            elif ui_name.endswith('_atnMsg'):
                self.uiList[ui_name].triggered.connect(getattr(self, ui_name[:-7]+"_message", partial(self.default_message,ui_name)))

    def default_action(self, ui_name):
        print("No action defined for this button: "+ui_name)
    def default_message(self, ui_name):
        msgName = ui_name[:-7]+"_msg"
        msg_txt = msgName + " is not defined in uiList."
        if msgName in self.uiList:
            msg_txt = self.uiList[msgName]
        tmpMsg = QtWidgets.QMessageBox()
        tmpMsg.setWindowTitle("Info")
        tmpMsg.setText(msg_txt)
        tmpMsg.addButton("OK",QtWidgets.QMessageBox.YesRole)
        tmpMsg.exec_()

    def input_choice(self, ui_name):
        if ui_name in self.uiList.keys():
            return self.uiList[ui_name].currentIndex()
        else:
            return None
    def output_text(self, ui_name, text):
        if ui_name in self.uiList.keys():
            self.uiList[ui_name].setText(text)

    def readFileData(self,file,binary=0):
        with open(file) as f:
            if binary == 0:
                data = json.load(f)
            else:
                data = _pickle.load(f)
        return data
    def writeFileData(self,data,file,binary=0):
        with open(file, 'w') as f:
            if binary == 0:
                json.dump(data, f)
            else:
                _pickle.dump(data, f)
    def readFileText(self, file):
        with open(file) as f:
            txt = f.read()
        return txt
    def writeFileText(self, txt, file):
        with open(file, 'w') as f:
            f.write(txt)
    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        quitAction = menu.addAction("Quit")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAction:
            self.close()

    def loadLang(self):
        if isinstance(self, QtWidgets.QMainWindow):
            self.quickMenu(['language_menu;&Language'])
            cur_menu = self.uiList['language_menu']
            self.quickMenuAction('langDefault_atnLang', 'Default','','langDefault.png', cur_menu)
            cur_menu.addSeparator()
            self.uiList['langDefault_atnLang'].triggered.connect(partial(self.setLang,'default'))
        self.memoData['lang']={}
        self.memoData['lang']['default']={}
        for ui_name in self.uiList:
            ui_element = self.uiList[ui_name]
            if type(ui_element) in [ QtWidgets.QLabel, QtWidgets.QPushButton, QtWidgets.QAction, QtWidgets.QCheckBox ]:
                self.memoData['lang']['default'][ui_name] = str(ui_element.text())
            elif type(ui_element) in [ QtWidgets.QGroupBox, QtWidgets.QMenu ]:
                self.memoData['lang']['default'][ui_name] = str(ui_element.title())
            elif type(ui_element) in [ QtWidgets.QTabWidget]:
                tabCnt = ui_element.count()
                tabNameList = []
                for i in range(tabCnt):
                    tabNameList.append(str(ui_element.tabText(i)))
                self.memoData['lang']['default'][ui_name]=';'.join(tabNameList)
            elif type(ui_element) == str:
                self.memoData['lang']['default'][ui_name] = self.uiList[ui_name]

        lang_path = os.path.dirname(self.location)
        baseName = os.path.splitext( os.path.basename(self.location) )[0]
        for fileName in os.listdir(lang_path):
            if fileName.startswith(baseName+"_lang_"):
                langName = fileName.replace(baseName+"_lang_","").split('.')[0].replace(" ","")
                self.memoData['lang'][ langName ] = self.readFileData( os.path.join(lang_path,fileName) )
                if isinstance(self, QtWidgets.QMainWindow):
                    self.quickMenuAction(langName+'_atnLang', langName.upper(),'',langName + '.png', self.uiList['language_menu'])
                    self.uiList[langName+'_atnLang'].triggered.connect(partial(self.setLang,langName))
        if isinstance(self, QtWidgets.QMainWindow) and len(self.memoData['lang']) == 1:
            self.quickMenuAction('langExport_atnLang', 'Export Default Language','','langExport.png', self.uiList['language_menu'])
            self.uiList['langExport_atnLang'].triggered.connect(self.exportLang)
    def setLang(self, langName):
        uiList_lang_read = self.memoData['lang'][langName]
        for ui_name in uiList_lang_read:
            ui_element = self.uiList[ui_name]
            if type(ui_element) in [ QtWidgets.QLabel, QtWidgets.QPushButton, QtWidgets.QAction, QtWidgets.QCheckBox ]:
                if uiList_lang_read[ui_name] != "":
                    ui_element.setText(uiList_lang_read[ui_name])
            elif type(ui_element) in [ QtWidgets.QGroupBox, QtWidgets.QMenu ]:
                if uiList_lang_read[ui_name] != "":
                    ui_element.setTitle(uiList_lang_read[ui_name])
            elif type(ui_element) in [ QtWidgets.QTabWidget]:
                tabCnt = ui_element.count()
                if uiList_lang_read[ui_name] != "":
                    tabNameList = uiList_lang_read[ui_name].split(';')
                    if len(tabNameList) == tabCnt:
                        for i in range(tabCnt):
                            if tabNameList[i] != "":
                                ui_element.setTabText(i,tabNameList[i])
            elif type(ui_element) == str:
                if uiList_lang_read[ui_name] != "":
                    self.uiList[ui_name] = uiList_lang_read[ui_name]
    def exportLang(self):
        file = QtWidgets.QFileDialog.getSaveFileName(self, "Export Default UI Language File","","RAW data (*.json);;AllFiles(*.*)")
        if isinstance(file, (list, tuple)):
            file = file[0]
        else:
            file = str(file)
        if not file == "":
            self.writeFileData( self.memoData['lang']['default'], file )
            self.quickMsg("Languge File created: '"+file)
    def quickMenu(self, ui_names):
        if isinstance(self, QtWidgets.QMainWindow):
            menubar = self.menuBar()
            for each_ui in ui_names:
                createOpt = each_ui.split(';')
                if len(createOpt) > 1:
                    uiName = createOpt[0]
                    uiLabel = createOpt[1]
                    self.uiList[uiName] = QtWidgets.QMenu(uiLabel)
                    menubar.addMenu(self.uiList[uiName])
        else:
            print("Warning (QuickMenu): Only QMainWindow can have menu bar.")

    def quickMenuAction(self, objName, title, tip, icon, menuObj):
        self.uiList[objName] = QtWidgets.QAction(QtGui.QIcon(icon), title, self)
        self.uiList[objName].setStatusTip(tip)
        menuObj.addAction(self.uiList[objName])

    def quickLayout(self, type, ui_name=""):
        the_layout = ''
        if type in ("form", "QFormLayout"):
            the_layout = QtWidgets.QFormLayout()
            the_layout.setLabelAlignment(QtCore.Qt.AlignLeft)
            the_layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        elif type in ("grid", "QGridLayout"):
            the_layout = QtWidgets.QGridLayout()
        elif type in ("hbox", "QHBoxLayout"):
            the_layout = QtWidgets.QHBoxLayout()
            the_layout.setAlignment(QtCore.Qt.AlignTop)
        else:
            the_layout = QtWidgets.QVBoxLayout()
            the_layout.setAlignment(QtCore.Qt.AlignTop)
        if ui_name != "":
            self.uiList[ui_name] = the_layout
        return the_layout

    def quickUI(self, part_list, parentObject="", insert_opt=""):
        if not isinstance(part_list, (list, tuple)):
            part_list = [part_list]
        ui_list = []
        ui_label_list = []
        form_type = 0
        for each_part in part_list:
            if isinstance(each_part, str):
                partInfo = each_part.split(';')
                uiNameLabel = partInfo[0].split('@')
                uiName = uiNameLabel[0]
                uiLabel = ''
                if len(uiNameLabel) > 1:
                    uiLabel = uiNameLabel[1]
                    form_type = 1
                uiType = partInfo[1] if len(partInfo) > 1 else ""
                uiArgs = partInfo[2] if len(partInfo) > 2 else ""
                if uiType == "":
                    print(uiType)
                    print("Warning (QuickUI): uiType is empty for "+each_part)
                else:
                    ui_create_state = 0
                    if not uiType[0] == 'Q':
                        self.uiList[uiName] = getattr(eval(uiType), uiType)()
                        ui_list.append(self.uiList[uiName])
                        ui_create_state = 1
                    else:
                        if uiType in ('QVBoxLayout', 'QHBoxLayout', 'QFormLayout', 'QGridLayout'):
                            ui_list.append(self.quickLayout(uiType, uiName))
                            ui_create_state = 1
                        elif uiType in ('QSplitter', 'QTabWidget', 'QGroupBox'):
                            if uiType == 'QSplitter':
                                split_type = QtCore.Qt.Horizontal
                                if uiArgs == 'v':
                                    split_type = QtCore.Qt.Vertical
                                self.uiList[uiName]=QtWidgets.QSplitter(split_type)
                                ui_list.append(self.uiList[uiName])
                                ui_create_state = 1
                            elif uiType == 'QTabWidget':
                                self.uiList[uiName]=QtWidgets.QTabWidget()
                                self.uiList[uiName].setStyleSheet("QTabWidget::tab-bar{alignment:center;}QTabBar::tab { min-width: 100px; }")
                                ui_list.append(self.uiList[uiName])
                                ui_create_state = 1
                            elif uiType == 'QGroupBox':
                                arg_list = [x.strip() for x in uiArgs.split(',')]
                                grp_layout = arg_list[0] if arg_list[0]!='' else 'vbox'
                                grp_title = arg_list[1] if len(arg_list)>1 else uiName
                                grp_layout = self.quickLayout(grp_layout, uiName+"_layout" )
                                self.uiList[uiName] = QtWidgets.QGroupBox(grp_title)
                                self.uiList[uiName].setLayout(grp_layout)
                                ui_list.append(self.uiList[uiName])
                                ui_create_state = 1
                        else:
                            if uiArgs == "":
                                self.uiList[uiName] = getattr(QtWidgets, uiType)()
                                ui_list.append(self.uiList[uiName])
                                ui_create_state = 1
                            else:
                                if not ( uiArgs.startswith("(") and uiArgs.endswith(")") ):
                                    self.uiList[uiName] = getattr(QtWidgets, uiType)(uiArgs)
                                    ui_list.append(self.uiList[uiName])
                                    ui_create_state = 1
                                else:
                                    arg_list = uiArgs.replace('(','').replace(')','').split(',')
                                    if uiType == 'QComboBox':
                                        self.uiList[uiName] = QtWidgets.QComboBox()
                                        self.uiList[uiName].addItems(arg_list)
                                        ui_list.append(self.uiList[uiName])
                                        ui_create_state = 1
                                    elif uiType == 'QTreeWidget':
                                        self.uiList[uiName] = QtWidgets.QTreeWidget()
                                        self.uiList[uiName].setHeaderLabels(arg_list)
                                        ui_list.append(self.uiList[uiName])
                                        ui_create_state = 1
                                    elif uiType == 'QSpacerItem':
                                        policyList = ( QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Ignored)
                                        arg_list = [ int(x) for x in arg_list ]
                                        self.uiList[uiName] = QtWidgets.QSpacerItem(arg_list[0],arg_list[1], policyList[arg_list[2]], policyList[arg_list[3]] )
                                        ui_list.append(self.uiList[uiName])
                                        ui_create_state = 1
                                    else:
                                        print("Warning (QuickUI): uiType don't support array arg for "+each_part)
                    if ui_create_state == 1:
                        if uiLabel != '':
                            ui_label_list.append((uiName,uiLabel))
                        else:
                            ui_label_list.append('')
                    ui_create_state = 0
            else:
                if isinstance(each_part, (QtWidgets.QWidget, QtWidgets.QLayout, QtWidgets.QSpacerItem)):
                    ui_list.append(each_part)
                    ui_label_list.append('')
                elif isinstance(each_part, (tuple, list)):
                    if len(each_part) != 0:
                        if isinstance(each_part[0], (tuple, list)) and len(each_part)==2:
                            ui_list.extend(each_part[0])
                            ui_label_list.extend(each_part[1])
                        else:
                            ui_list.extend(each_part)
                            ui_label_list.extend(['']*len(each_part))

        if parentObject == '':
            if form_type == 1:
                return [ui_list, ui_label_list]
            else:
                return ui_list
        else:
            if isinstance(parentObject, str):
                parentName = ''
                parentType = ''
                parentArgs = ''
                layout_type_list = (
                    'QVBoxLayout', 'QHBoxLayout', 'QFormLayout', 'QGridLayout', 'vbox', 'hbox', 'grid', 'form',
                    'QSplitter', 'QTabWidget', 'QGroupBox', 'split', 'tab', 'grp',
                )
                parentOpt = parentObject.split(';')
                if len(parentOpt) == 1:
                        parentName = parentOpt[0]
                        parentType = parentName.rsplit('_',1)[-1]
                elif len(parentOpt)==2:
                    parentName = parentOpt[0]
                    if parentOpt[1] in layout_type_list:
                        parentType = parentOpt[1]
                    else:
                        parentType = parentName.rsplit('_',1)[-1]
                        parentArgs = parentOpt[1]
                elif len(parentOpt)>=3:
                    parentName = parentOpt[0]
                    parentType = parentOpt[1]
                    parentArgs = parentOpt[2]
                if parentName=='' or (parentType not in layout_type_list):
                    print("Warning (QuickUI): quickUI not support parent layout as "+parentObject)
                    return
                else:
                    if parentType in ('QVBoxLayout', 'QHBoxLayout', 'QFormLayout', 'QGridLayout', 'vbox', 'hbox', 'grid', 'form'):
                        parentObject = self.quickLayout(parentType, parentName)
                    elif parentType in ('QSplitter', 'QTabWidget', 'QGroupBox', 'split', 'tab', 'grp'):
                        if parentType in ('QSplitter', 'split'):
                            split_type = QtCore.Qt.Horizontal
                            if parentArgs == 'v':
                                split_type = QtCore.Qt.Vertical
                            self.uiList[parentName]=QtWidgets.QSplitter(split_type)
                            parentObject = self.uiList[parentName]
                        elif parentType in ('QTabWidget', 'tab'):
                            self.uiList[parentName]=QtWidgets.QTabWidget()
                            self.uiList[parentName].setStyleSheet("QTabWidget::tab-bar{alignment:center;}QTabBar::tab { min-width: 100px; }")
                            parentObject = self.uiList[parentName]
                        elif parentType in ('QGroupBox', 'grp'):
                            arg_list = [x.strip() for x in parentArgs.split(',')]
                            grp_layout = arg_list[0] if arg_list[0]!='' else 'vbox'
                            grp_title = arg_list[1] if len(arg_list)>1 else parentName
                            grp_layout = self.quickLayout(grp_layout, parentName+"_layout" )
                            self.uiList[parentName] = QtWidgets.QGroupBox(grp_title)
                            self.uiList[parentName].setLayout(grp_layout)
                            parentObject = self.uiList[parentName]

            parentLayout = ''
            if isinstance(parentObject, QtWidgets.QLayout):
                parentLayout = parentObject
            elif isinstance(parentObject, QtWidgets.QGroupBox):
                parentLayout = parentObject.layout()
            if isinstance(parentLayout, QtWidgets.QBoxLayout):
                for each_ui in ui_list:
                    if isinstance(each_ui, QtWidgets.QWidget):
                        parentLayout.addWidget(each_ui)
                    elif isinstance(each_ui, QtWidgets.QSpacerItem):
                        parentLayout.addItem(each_ui)
                    elif isinstance(each_ui, QtWidgets.QLayout):
                        parentLayout.addLayout(each_ui)
            elif isinstance(parentLayout, QtWidgets.QGridLayout):
                insertRow = parentLayout.rowCount()
                insertCol = parentLayout.columnCount()
                for i in range(len(ui_list)):
                    each_ui = ui_list[i]
                    x = insertRow if insert_opt=="h" else i
                    y = i if insert_opt=="h" else insertCol
                    if isinstance(each_ui, QtWidgets.QWidget):
                        parentLayout.addWidget(each_ui,x,y)
                    elif isinstance(each_ui, QtWidgets.QSpacerItem):
                        parentLayout.addItem(each_ui,x,y)
                    elif isinstance(each_ui, QtWidgets.QLayout):
                        parentLayout.addLayout(each_ui,x,y)
            elif isinstance(parentLayout, QtWidgets.QFormLayout):
                for i in range(len(ui_list)):
                    each_ui = ui_list[i]
                    if isinstance(each_ui, QtWidgets.QWidget) or isinstance(each_ui, QtWidgets.QLayout):
                        if ui_label_list[i] != '':
                            uiLabelName = ui_label_list[i][0] + "_label"
                            uiLabelText = ui_label_list[i][1]
                            self.uiList[uiLabelName] = QtWidgets.QLabel(uiLabelText)
                            parentLayout.addRow(self.uiList[uiLabelName], each_ui)
                        else:
                            parentLayout.addRow(each_ui)
            else:
                if isinstance(parentObject, QtWidgets.QSplitter):
                    for each_ui in ui_list:
                        if isinstance(each_ui, QtWidgets.QWidget):
                            parentObject.addWidget(each_ui)
                        else:
                            tmp_holder = QtWidgets.QWidget()
                            tmp_holder.setLayout(each_ui)
                            parentObject.addWidget(tmp_holder)
                elif isinstance(parentObject, QtWidgets.QTabWidget):
                    tab_names = insert_opt.replace('(','').replace(')','').split(',')
                    for i in range( len(ui_list) ):
                        each_tab = ui_list[i]
                        each_name = 'tab_'+str(i)
                        if i < len(tab_names):
                            if tab_names[i] != '':
                                each_name = tab_names[i]
                        if isinstance(each_tab, QtWidgets.QWidget):
                            parentObject.addTab(each_tab, each_name)
                        else:
                            tmp_holder = QtWidgets.QWidget()
                            tmp_holder.setLayout(each_tab)
                            parentObject.addTab(tmp_holder, each_name)
            return parentObject
    def quickSplitUI(self, name, part_list, type):
        split_type = QtCore.Qt.Horizontal
        if type == 'v':
            split_type = QtCore.Qt.Vertical
        self.uiList[name]=QtWidgets.QSplitter(split_type)

        for each_part in part_list:
            if isinstance(each_part, QtWidgets.QWidget):
                self.uiList[name].addWidget(each_part)
            else:
                tmp_holder = QtWidgets.QWidget()
                tmp_holder.setLayout(each_part)
                self.uiList[name].addWidget(tmp_holder)
        return self.uiList[name]

    def quickTabUI(self, name, tab_list, tab_names):
        self.uiList[name]=QtWidgets.QTabWidget()
        self.uiList[name].setStyleSheet("QTabWidget::tab-bar{alignment:center;}QTabBar::tab { min-width: 100px; }")
        for i in range( len(tab_list) ):
            each_tab = tab_list[i]
            each_name = tab_names[i]
            if isinstance(each_tab, QtWidgets.QWidget):
                self.uiList[name].addTab(each_tab, each_name)
            else:
                tmp_holder = QtWidgets.QWidget()
                tmp_holder.setLayout(each_tab)
                self.uiList[name].addTab(tmp_holder, each_name)
        return self.uiList[name]

    def quickGrpUI(self, ui_name, ui_label, ui_layout):
        self.uiList[ui_name] = QtWidgets.QGroupBox(ui_label)
        if isinstance(ui_layout, QtWidgets.QLayout):
            self.uiList[ui_name].setLayout(ui_layout)
        elif isinstance(ui_layout, str):
            ui_layout = self.quickLayout(ui_name+"_layout", ui_layout)
            self.uiList[ui_name].setLayout(ui_layout)
        return [self.uiList[ui_name], ui_layout]

    def quickPolicy(self, ui_list, w, h):
        if not isinstance(ui_list, (list, tuple)):
            ui_list = [ui_list]
        policyList = ( QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Ignored)
        for each_ui in ui_list:
            if isinstance(each_ui, str):
                each_ui = self.uiList[each_ui]
            each_ui.setSizePolicy(policyList[w],policyList[h])

    def quickInfo(self, info):
        self.statusBar().showMessage(info)
    def quickMsg(self, msg):
        tmpMsg = QtWidgets.QMessageBox()
        tmpMsg.setWindowTitle("Info")
        tmpMsg.setText(msg)
        tmpMsg.addButton("OK",QtWidgets.QMessageBox.YesRole)
        tmpMsg.exec_()
    def quickMsgAsk(self, msg, mode=0, choice=[]):
        modeOpt = (QtWidgets.QLineEdit.Normal, QtWidgets.QLineEdit.NoEcho, QtWidgets.QLineEdit.Password, QtWidgets.QLineEdit.PasswordEchoOnEdit)
        if len(choice)==0:
            txt, ok = QtWidgets.QInputDialog.getText(self, "Input", msg, modeOpt[mode])
            return (unicode(txt), ok)
        else:
            txt, ok = QtWidgets.QInputDialog.getItem(self, "Input", msg, choice, 0, 0)
            return (unicode(txt), ok)
    def quickFileAsk(self, type):
        file = ""
        if type == 'export':
            file = QtWidgets.QFileDialog.getSaveFileName(self, "Save File","","RAW data (*.json);;RAW binary data(*.dat);;Format Txt(*{0});;AllFiles(*.*)".format(self.fileType))
        elif type == 'import':
            file = QtWidgets.QFileDialog.getOpenFileName(self, "Open File","","RAW data (*.json);;RAW binary data(*.dat);;Format Txt(*{});;AllFiles(*.*)".format(self.fileType))
        if isinstance(file, (list, tuple)):
            file = file[0]
        else:
            file = unicode(file)
        return file


class NSOMonitor(NSO):
    def __init__(self, parent=None, mode=0):
        NSO.__init__(self, parent)

        self.version="0.1"
        self.mode = 0
        if mode in [0,1]:
            self.mode = mode
        self.memoData['data']=[]

        self.setupStyle()
        if isinstance(self, QtWidgets.QMainWindow):
            self.setupMenu()
        self.setupWin()
        self.setupUI()
        self.Establish_Connections()
        self.loadData()
        self.loadLang()

    def setupMenu(self):
        self.quickMenu(['file_menu;&File','setting_menu;&Setting','help_menu;&Help'])
        cur_menu = self.uiList['setting_menu']
        self.quickMenuAction('setParaA_atn','Set Parameter &A','A example of tip notice.','setParaA.png', cur_menu)
        self.uiList['setParaA_atn'].setShortcut(QtGui.QKeySequence("Ctrl+R"))
        cur_menu.addSeparator()
        super(self.__class__,self).setupMenu()

    def setupWin(self):
        super(self.__class__,self).setupWin()
        self.setGeometry(2000, 2000, 1000, 1000)

    def setupUI(self):
        super(self.__class__,self).setupUI()

        self.qui('source_txt | process_btn;Start Parsing', 'upper_vbox')
        self.qui('upper_vbox | result_txt', 'input_split;v')
        self.qui('filePath_input | fileLoad_btn;Load | fileExport_btn;Export', 'fileBtn_layout;hbox')
        self.qui('input_split | fileBtn_layout', 'main_layout')

        keep_margin_layout = ['main_layout']
        for name, each in self.uiList.items():
            if isinstance(each, QtWidgets.QLayout) and name not in keep_margin_layout and not name.endswith('_grp_layout'):
                each.setContentsMargins(0, 0, 0, 0)
        self.quickInfo('Ready')

    def Establish_Connections(self):
        super(self.__class__,self).Establish_Connections()

    def loadData(self):
        print("Load data")

    def process_action(self):
        print("Process ....")
        source_txt = unicode(self.uiList['source_txt'].toPlainText())
        self.memoData['data'] = [row.strip() for row in source_txt.split('\n')]
        print("Update Result")
        txt='\n'.join([('>>: '+row) for row in self.memoData['data']])
        self.uiList['result_txt'].setText(txt)

    def font_action(self):
        font, ok = QtWidgets.QFontDialog.getFont()
        if ok:
            self.uiList['font_label'].setFont(font)

    def fileExport_action(self):
        filePath_input = self.uiList['filePath_input']
        file = unicode(filePath_input.text())
        if file == "":
            file= self.quickFileAsk('export')
        if file == "":
            return
        filePath_input.setText(file)
        ui_data = unicode(self.uiList['source_txt'].toPlainText())
        if file.endswith('.dat'):
            self.writeFileData(ui_data, file, binary=1)
        else:
            self.writeFileData(ui_data, file)
        self.quickInfo("File: '"+file+"' creation finished.")

    def fileLoad_action(self):
        filePath_input = self.uiList['filePath_input']
        file=unicode(filePath_input.text())
        if file == "":
            file= self.quickFileAsk('import')
        if file == "":
            return
        filePath_input.setText(file)
        ui_data = ""
        if file.endswith('.dat'):
            ui_data = self.readFileData(file, binary=1)
        else:
            ui_data = self.readFileData(file)
        self.uiList['source_txt'].setText(ui_data)
        self.quickInfo("File: '"+file+"' loading finished.")

single_NSOMonitor = None
def main(mode=0):
    app = QtWidgets.QApplication(sys.argv)
    global single_NSOMonitor
    if single_NSOMonitor is None:
        single_NSOMonitor = NSOMonitor()
    single_NSOMonitor.show()
    ui = single_NSOMonitor
    sys.exit(app.exec_())
    return ui

if __name__ == "__main__":
    main()
