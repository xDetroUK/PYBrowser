from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QTreeView, QAbstractItemView, QPushButton, QLabel, QHBoxLayout, QComboBox, \
    QLineEdit, QVBoxLayout
from BrowserFiles.browserPlugins.LilHelper import lilFuncs as dB


class TreeViewWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Create a QStandardItemModel and set it to the TreeView
        self.model = QStandardItemModel()
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.selection_model = self.tree_view.selectionModel()
        self.selection_model.selectionChanged.connect(self.onSelectionChanged)
        # Create the buttons
        add_button = QPushButton(QIcon('add_icon.png'), 'Add')
        add_button.clicked.connect(self.addDatatoDb)

        edit_button = QPushButton(QIcon('edit_icon.png'), 'Show')
        edit_button.clicked.connect(self.showData)


        remove_button = QPushButton(QIcon('remove_icon.png'), 'Remove')
        remove_button.clicked.connect(self.delitem)

        modify_button = QPushButton(QIcon('modify_icon.png'), 'Search')
        modify_button.clicked.connect(self.SearFromDatabase)

        # Create a QLabel widget for displaying the photo
        self.photo_label = QLabel(self)

        self.model.setColumnCount(4)
        self.model.setHeaderData(0, Qt.Horizontal, "ID")
        self.model.setHeaderData(1, Qt.Horizontal, "Name")
        self.model.setHeaderData(2, Qt.Horizontal, "Description")
        self.model.setHeaderData(3, Qt.Horizontal, "Use")



        # Create the layout and add the buttons, TreeView and photo
        button_layout = QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(modify_button)
        # Create the top row layout with the combo box and line edit
        top_row_layout = QHBoxLayout()
        self.combo_box = QComboBox()
        self.combo_box.currentIndexChanged.connect(self.showData)
        for tablenames in dB.showTables():
            self.combo_box.addItem(tablenames[0])
        top_row_layout.addWidget(self.combo_box)
        self.line_edit = QLineEdit()
        self.line_edit.returnPressed.connect(self.SearFromDatabase)
        top_row_layout.addWidget(self.line_edit)

        # Create the main layout and add the top row, button layout, TreeView, and photo
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_row_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.tree_view)
        main_layout.addWidget(self.photo_label)

        self.setLayout(main_layout)

        # Load the image and set it to the photo label
        self.pixmap = QPixmap(600,600)
    def SearFromDatabase(self):
        self.model.clear()
        srchdata = dB.searchDataFromAllTables(self.line_edit.text())
        for x in srchdata:
            id_item = QStandardItem(x[0])
            name_item = QStandardItem(x[1])
            description_item = QStandardItem(x[2])
            use_item = QStandardItem("Item Use")
            # Add the items to the model
            self.model.appendRow([id_item, name_item, description_item, use_item])
    def showData(self):
        # Create the QStandardItem objects for each cell in the row
        self.model.clear()
        xf = dB.showData(table=self.combo_box.currentText())
        for x in xf:
            id_item = QStandardItem(x[0])
            name_item = QStandardItem(x[1])
            description_item = QStandardItem(x[2])
            use_item = QStandardItem("Item Use")
            # Add the items to the model
            self.model.appendRow([id_item, name_item, description_item, use_item])
    def addDatatoDb(self):
        dB.cropScreenshot(self.combo_box.currentText(),mode='database')
    def onSelectionChanged(self, selected):
        try:
            indexes = selected.indexes()
            crname = self.model.itemFromIndex(indexes[1])
            self.curselect = crname.text()
            self.photo_label.setPixmap(dB.return_image(self.curselect))
        except:
            pass
    def delitem(self):
        dB.deleteRec(self.combo_box.currentText(),self.curselect)
        self.showData()