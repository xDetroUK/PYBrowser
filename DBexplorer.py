import sqlite3
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtSql import QSqlTableModel, QSqlDatabase
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QSplitter, QTreeView, QTableView, QPushButton, QWidget, QMenu, \
    QMessageBox, QInputDialog, QDialog, QFormLayout, QLineEdit, QFileDialog, QLabel, QComboBox, QApplication


class DatabaseExplorer(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("SQLite Database Explorer")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.splitter = QSplitter(Qt.Horizontal)

        self.treeView = QTreeView()
        self.treeView.clicked.connect(self.onTreeViewItemClicked)
        self.splitter.addWidget(self.treeView)

        self.tableView = QTableView()
        self.splitter.addWidget(self.tableView)

        layout.addWidget(self.splitter)

        self.loadButton = QPushButton("Load Database")
        self.loadButton.clicked.connect(self.loadDatabase)
        layout.addWidget(self.loadButton)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.showContextMenu)

        self.tableView.verticalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.verticalHeader().customContextMenuRequested.connect(self.showRowContextMenu)
    def showContextMenu(self, position):
        # Check if the right-clicked position corresponds to a valid index
        index = self.treeView.indexAt(position)

        contextMenu = QMenu(self)

        if index.isValid():
            # Existing behavior for when a table is selected
            selected_table = index.data()
            addAction = contextMenu.addAction("Add")
            deleteAction = contextMenu.addAction("Delete")
            addAction.triggered.connect(self.addColumn)
            deleteAction.triggered.connect(self.deleteTable)
        else:
            # New behavior for when clicked in an empty area
            addTableAction = contextMenu.addAction("Add Table")
            addTableAction.triggered.connect(self.addTable)

        contextMenu.exec_(self.treeView.viewport().mapToGlobal(position))
    def showRowContextMenu(self, position):
        # Get the row index from the position
        row = self.tableView.verticalHeader().logicalIndexAt(position)

        contextMenu = QMenu(self)
        deleteRowAction = contextMenu.addAction("Delete Row")
        deleteRowAction.triggered.connect(lambda: self.deleteTableRow(row))

        contextMenu.exec_(self.tableView.verticalHeader().mapToGlobal(position))
    def deleteTableRow(self, row):
        if row == -1:
            return

        # Get the selected table
        selected_table = self.treeView.currentIndex().data()
        if not selected_table:
            return

        # Prompt the user for confirmation
        reply = QMessageBox.question(self, 'Delete Row',
                                     f"Are you sure you want to delete the selected row from the table '{selected_table}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Connect to the SQLite database
            conn = sqlite3.connect(self.db.databaseName())
            cursor = conn.cursor()

            # Get the primary key column name
            cursor.execute(f"PRAGMA table_info({selected_table})")
            columns_info = cursor.fetchall()
            primary_key_column = next((col[1] for col in columns_info if col[5] == 1), None)
            if not primary_key_column:
                QMessageBox.warning(self, "Database Error", "Table does not have a primary key.")
                return

            # Get the primary key value of the selected row
            primary_key_value = self.tableView.model().record(row).value(primary_key_column)

            try:
                # Delete the row
                cursor.execute(f"DELETE FROM {selected_table} WHERE {primary_key_column} = ?", (primary_key_value,))
                conn.commit()
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Database Error", str(e))
            finally:
                conn.close()

            # Refresh the table view to reflect the changes
            self.showTableData(selected_table)
    def addTable(self):
        # Ask for the number of columns
        num_columns, ok = QInputDialog.getInt(self, "Add Table", "Enter number of columns:", 1, 1, 100, 1)
        if not ok:
            return

        # Create a dialog with input fields for table name, column names, and their types
        dialog = QDialog(self)
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Input for table name
        table_name_input = QLineEdit()
        form_layout.addRow("Table Name:", table_name_input)

        column_name_inputs = []
        column_type_inputs = []
        for i in range(num_columns):
            # Input for column name
            column_name_input = QLineEdit()
            column_name_inputs.append(column_name_input)
            form_layout.addRow(f"Column {i + 1} Name:", column_name_input)

            # Dropdown for column type
            column_type_input = QComboBox()
            column_type_input.addItems(["TEXT", "BLOB", "INT", "REAL", "NUMERIC"])
            column_type_inputs.append(column_type_input)
            form_layout.addRow(f"Column {i + 1} Type:", column_type_input)

        layout.addLayout(form_layout)

        # Add submit button
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(dialog.accept)
        layout.addWidget(submit_button)

        dialog.setLayout(layout)
        result = dialog.exec_()

        if result == QDialog.Accepted:
            table_name = table_name_input.text()
            columns = [f"{column_name_input.text()} {column_type_input.currentText()}" for
                       column_name_input, column_type_input in zip(column_name_inputs, column_type_inputs)]

            # Create the table in the database
            columns_str = ', '.join(columns)
            conn = sqlite3.connect(self.db.databaseName())
            cursor = conn.cursor()
            try:
                cursor.execute(f"CREATE TABLE {table_name} ({columns_str})")
                conn.commit()
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Database Error", str(e))
            finally:
                conn.close()

            # Refresh the tree view to show the new table
            self.populateTreeView(self.db.databaseName())
    def addColumn(self):
        # Get the selected table
        selected_table = self.treeView.currentIndex().data()
        if not selected_table:
            return

        # Connect to the SQLite database
        conn = sqlite3.connect(self.db.databaseName())
        cursor = conn.cursor()

        # Fetch column names and types for the selected table
        cursor.execute(f"PRAGMA table_info({selected_table})")
        columns_info = cursor.fetchall()
        column_details = [(col[1], col[2]) for col in columns_info]  # [(name, type), ...]

        # Create a dialog with input fields for each column
        dialog = QDialog(self)
        layout = QVBoxLayout()

        inputs = {}
        for column_name, column_type in column_details:
            label = QLabel(f"Enter value for {column_name} ({column_type}):")
            line_edit = QLineEdit()
            inputs[column_name] = line_edit
            layout.addWidget(label)
            layout.addWidget(line_edit)

        # Add submit button
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(dialog.accept)
        layout.addWidget(submit_button)

        dialog.setLayout(layout)
        result = dialog.exec_()

        if result == QDialog.Accepted:
            values = [line_edit.text() for line_edit in inputs.values()]

            # Insert the new row into the table
            placeholders = ', '.join(['?'] * len(values))
            try:
                cursor.execute(f"INSERT INTO {selected_table} VALUES ({placeholders})", values)
                conn.commit()
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Database Error", str(e))
            finally:
                conn.close()

            # Refresh the table view to show the updated data
            self.showTableData(selected_table)
    def deleteTable(self):
        # Get the selected table
        selected_table = self.treeView.currentIndex().data()
        if not selected_table:
            return

        # Prompt the user for confirmation
        reply = QMessageBox.question(self, 'Delete Table',
                                     f"Are you sure you want to delete the table '{selected_table}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Connect to the SQLite database
            conn = sqlite3.connect(self.db.databaseName())
            cursor = conn.cursor()

            try:
                # Drop the table
                cursor.execute(f"DROP TABLE {selected_table}")
                conn.commit()
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Database Error", str(e))
            finally:
                conn.close()

            # Refresh the tree view to reflect the changes
            self.populateTreeView(self.db.databaseName())
    def loadDatabase(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, "Open SQLite Database", "", "SQLite Databases (*.db);;All Files (*)", options=options)
        if filePath:
            self.db = QSqlDatabase.addDatabase("QSQLITE")
            self.db.setDatabaseName(filePath)
            if not self.db.open():
                print("Error: connection with database failed")
            else:
                self.populateTreeView(filePath)
    def populateTreeView(self, dbPath):
        # Connect to the SQLite database
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()

        # Fetch all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['Name'])

        for table in tables:
            table_name = table[0]
            table_item = QStandardItem(table_name)
            model.appendRow(table_item)

        self.treeView.setModel(model)

        # Close the database connection
        conn.close()
    def onTreeViewItemClicked(self, index):
        table_name = index.data()
        self.showTableData(table_name)
    def showTableData(self, table_name):
        model = QSqlTableModel(db=self.db)
        model.setTable(table_name)
        model.select()
        self.tableView.setModel(model)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DatabaseExplorer()
    window.show()
    sys.exit(app.exec_())