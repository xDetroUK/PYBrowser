from datetime import datetime
import sys, qtmodern.styles
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from BrowserFiles.browserPlugins.chessFiles import chessGUI
from BrowserFiles.browserPlugins.LilHelper import lilHelperGUI
from AIFiles import Niv

class WebEnginePage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            return True
        return super(WebEnginePage, self).acceptNavigationRequest(url, _type, isMainFrame)


class HtmlView(QWebEngineView):
    def __init__(self, main_window):
        super(HtmlView, self).__init__()
        self.setPage(WebEnginePage(self))
        self.main_window = main_window
        self.load(QUrl("https://google.com"))
        self.titleChanged.connect(self.update_tab_name)
        self.urlChanged.connect(self.update_url_input)
#        self.chessGUI = chessGUI.ChessMainGUI()

    def createWindow(self, _type):
        if _type == QWebEnginePage.WebBrowserTab:
            return self.main_window.new_tab()
        return None

    def set_url(self, url):
        self.load(QUrl(url))

    def update_tab_name(self, title):
        parent_tab = self.parent()
        parent_widget = parent_tab.parent().parent()  # Access the actual QTabWidget
        current_index = parent_widget.indexOf(parent_tab)
        tab_name = title[:12] if len(title) > 12 else title
        parent_widget.setTabText(current_index, tab_name)

    def update_url_input(self, qurl):
        parent_tab = self.parent()
        url_input = parent_tab.findChild(QLineEdit, "url_input")
        ytButton = parent_tab.findChild(QPushButton, "ytdownload")  # Get the ytdownload button
        url_input.setText(qurl.toString())
        self.main_window.save_history(qurl.toString())
        # Check if the domain is "www.youtube.com" or "youtube.com"
        if "youtube.com" in qurl.toString():
            ytButton.setHidden(False)  # Show the button

        else:
            ytButton.setHidden(True)  # Hide the button

        try:

            if self.main_window.is_bookmarked(qurl.toString()):

                self.main_window.star_button.setText("★")
            else:
                self.main_window.star_button.setText("☆")
        except:
            pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.chesswid = chessGUI.ChessMainGUI()
        self.chatwid = Niv.ChatWidget()
        self.treeviewwid = lilHelperGUI.TreeViewWidget()
        self.niv =" dB.Niamh()"
        #  self.DwUpspeedtest = SpeedTestApp()
        self.databaseExp = "DatabaseExplorer()"
        self.SSHfileb = "SSHFileBrowser()"
        self.img_windows = []

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        self.setMouseTracking(True)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        self.browser_history = []
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Web `Browser`')
        self.setGeometry(100, 100, 800, 600)
        self.tree_model = QStandardItemModel()
        self.bookmarks_item = QStandardItem("Bookmarks")
        self.history_item = QStandardItem("History")
        self.tree_model.appendRow(self.bookmarks_item)
        self.tree_model.appendRow(self.history_item)
        self.tree_view = QTreeView(self)
        self.tree_view.doubleClicked.connect(self.on_item_double_clicked)

        self.tree_view.setModel(self.tree_model)
        self.tree_view.setFixedSize(300, 300)
        self.tree_view.hide()  # Initially hidden

        self.bookhistorybutton = QPushButton("🌲")
        self.bookhistorybutton.setFixedSize(20, 20)
        self.bookhistorybutton.clicked.connect(self.bookmarkswidet)

        minimize_button = QPushButton('─')
        minimize_button.setFixedSize(20, 20)
        minimize_button.clicked.connect(self.showMinimized)

        fullscreen_button = QPushButton('☐')
        fullscreen_button.setFixedSize(20, 20)
        fullscreen_button.setCheckable(True)
        fullscreen_button.clicked.connect(self.toggleFullscreen)

        close_button = QPushButton('x')
        close_button.setFixedSize(20, 20)
        close_button.clicked.connect(self.close)

        # Create a widget and layout for the corner buttons
        titlebar_widget = QWidget()
        titlebar_layout = QHBoxLayout(titlebar_widget)
        titlebar_layout.setSpacing(5)
        titlebar_layout.setContentsMargins(0, 0, 0, 0)  # No margins
        titlebar_layout.addWidget(self.bookhistorybutton)
        titlebar_layout.addWidget(minimize_button)
        titlebar_layout.addWidget(fullscreen_button)
        titlebar_layout.addWidget(close_button)

        # Set the widget with the buttons as the corner widget
        self.tab_widget.setCornerWidget(titlebar_widget, Qt.TopRightCorner)

        self.new_tab()

    def save_bookmark(self, url):
        with open("BrowserFiles/data/bookmarks.txt", "a") as file:
            file.write(f"{url}\n")

    def load_bookmarks(self):
        with open("BrowserFiles/data/bookmarks.txt", "r") as file:
            bookmarks = file.readlines()
        return [bookmark.strip() for bookmark in bookmarks]

    def is_bookmarked(self, url):
        return url in self.load_bookmarks()

    def remove_bookmark(self, url):
        bookmarks = self.load_bookmarks()
        bookmarks.remove(url)
        with open("BrowserFiles/data/bookmarks.txt", "w") as file:
            for bookmark in bookmarks:
                file.write(f"{bookmark}\n")

    def save_history(self, url):
        with open("BrowserFiles/data/history.txt", "a") as file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            file.write(f"{timestamp} - {url}\n")

    def show_browser_history(self):
        # Read browser history from file
        with open("BrowserFiles/data/history.txt", "r") as file:
            history_data = file.readlines()

        self.browser_history = [line.strip().split(" - ") for line in history_data if line.strip()]

        # Create a dialog to show the browser history
        history_dialog = QDialog(self)
        history_dialog.setWindowTitle("Browser History")
        history_dialog.setGeometry(100, 100, 600, 300)
        layout = QVBoxLayout(history_dialog)

        list_widget = QListWidget(history_dialog)

        for data in self.browser_history:
            if len(data) == 2:  # Check if we have two elements
                timestamp, url = data
                # Display only the timestamp and URL in the list
                display_text = f"{timestamp} - {url}"
                list_item = QListWidgetItem(display_text)
                list_item.setData(Qt.UserRole, url)
                list_widget.addItem(list_item)
            else:
                print(f"Unexpected line format: {' - '.join(data)}")

        list_widget.itemDoubleClicked.connect(self.load_history_item)

        layout.addWidget(list_widget)
        history_dialog.setLayout(layout)
        history_dialog.exec_()

    def load_history_item(self, item):
        url = item.data(Qt.UserRole)
        browser_view = self.new_tab()
        browser_view.set_url(url)

    def new_tab(self):
        tab_layout = QVBoxLayout()
        self.star_button = QPushButton("☆")  # Start with a non-bookmarked state
        self.star_button.setFixedSize(20, 20)
        self.star_button.clicked.connect(self.toggle_bookmark)

        back_button = QPushButton('Back')
        back_button.setFixedSize(20, 20)
        back_button.clicked.connect(self.current_tab_go_back)

        home_button = QPushButton('Home')
        home_button.setFixedSize(20, 20)
        home_button.clicked.connect(self.current_tab_go_home)

        forward_button = QPushButton('Forward')
        forward_button.setFixedSize(20, 20)
        forward_button.clicked.connect(self.current_tab_go_forward)

        url_input = QLineEdit()
        url_input.setObjectName("url_input")
        url_input.returnPressed.connect(self.current_tab_load_url)

        ytdownload = QPushButton("YT")
        ytdownload.clicked.connect(self.ytdownload)
        ytdownload.setFixedSize(20, 20)
        ytdownload.setHidden(True)
        ytdownload.setObjectName("ytdownload")

        self.menubtn = QMenu(self)
        self.toolsmenu = QMenu("Tools", self)
        self.VPNmenu = QMenu("VPN", self)

        self.menubtn.addAction("Chess", self.showchessscr)

        self.menubtn.addAction("Chat", self.showchatwid)

        self.menubtn.addAction("LilHelper", self.showtreeview)

        self.menubtn.addAction("History", self.show_browser_history)

        self.menubtn.addMenu(self.VPNmenu)

        self.toolsmenu.addAction("CPU Monitor", self.showusagemonitor)

#        self.toolsmenu.addAction("Image Variations", self.editAIimage)

        #self.toolsmenu.addAction("Picture coordinates", lambda: dB.cropScreenshot(mode='cords', image_path=
        #QFileDialog.getOpenFileName(self, "Select a PNG file", "", "PNG Files (*.png)")[0]))

#        self.toolsmenu.addAction("Test IPs", self.checkips)

        self.toolsmenu.addAction("Database Explorer", self.showdatabaseex)

#        self.toolsmenu.addAction("Create new database", self.createDatabase)

        self.toolsmenu.addAction("SSH File Manager", self.showSSHfilebrowser)

        self.toolsmenu.addAction("Speed Test", self.speedTest)

#        self.VPNmenu.addAction("Reset", self.reset_proxy)

        self.menubtn.addMenu(self.toolsmenu)


        menu_button = QToolButton(self)
        menu_button.setText("⚙️")  # or set an icon here
        menu_button.setMenu(self.menubtn)
        menu_button.setPopupMode(QToolButton.InstantPopup)

        toolbar_layout = QHBoxLayout()
        toolbar_layout.addWidget(back_button)
        toolbar_layout.addWidget(home_button)
        toolbar_layout.addWidget(forward_button)
        toolbar_layout.addWidget(url_input)
        toolbar_layout.addWidget(self.star_button)
        toolbar_layout.addWidget(ytdownload)
        toolbar_layout.addWidget(menu_button)

        tab_layout.addLayout(toolbar_layout)
        browser_view = HtmlView(self)
        tab_layout.addWidget(browser_view)

        tab = QWidget()
        tab.setLayout(tab_layout)

        self.tab_widget.addTab(tab, 'New Tab')
        self.tab_widget.setCurrentWidget(tab)

        return browser_view  # Return the view for the createWindow method

    def toggle_bookmark(self):
        current_url = self.current_url_input().text().strip()
        if self.is_bookmarked(current_url):
            self.remove_bookmark(current_url)
            self.star_button.setText("☆")  # Update to non-bookmarked state
        else:
            self.save_bookmark(current_url)
            self.star_button.setText("★")  # Update to bookmarked state

    def showchessscr(self):
        self.chesswid.show()

    def speedTest(self):
        self.DwUpspeedtest.show()

    def showSSHfilebrowser(self):
        self.SSHfileb.show()

    def showusagemonitor(self):
        self.monitor = "ProcessMonitor()"
        self.monitor.show()

    def showchatwid(self):
        self.chatwid.show()

    def showtreeview(self):
        self.treeviewwid.show()

    def showdatabaseex(self):
        self.databaseExp.show()
    def toggleFullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def close_tab(self, index):
        """
        Close the tab at the specified index and delete its content.
        """
        if self.tab_widget.count() <= 1:  # if it's the last tab
            return

        # Get the widget in the tab (i.e., the browser view)
        tab_content = self.tab_widget.widget(index)

        # Remove the tab
        self.tab_widget.removeTab(index)

        # Delete the tab content
        if tab_content:
            tab_content.deleteLater()

    def current_tab(self):
        return self.tab_widget.currentWidget()

    def current_view(self):
        tab = self.current_tab()
        return tab.findChild(HtmlView)

    def current_url_input(self):
        tab = self.current_tab()
        return tab.findChild(QLineEdit, "url_input")

    def ytdownload(self):
        current_url = self.current_url_input().text().strip()
        #threading.Thread(target=dB.ytDownloadMp3, args=(current_url,)).start()

    def current_tab_go_back(self):
        self.current_view().back()

    def current_tab_go_home(self):
        self.current_view().load(QUrl("https://google.com"))

    def current_tab_go_forward(self):
        self.current_view().forward()

    def current_tab_load_url(self):
        view = self.current_view()
        url_input = self.current_url_input()
        url_text = url_input.text().strip()

        if not url_text.lower().startswith(('http://', 'https://', 'www.')):
            url_text = f'https://www.{url_text}'
        elif url_text.lower().startswith('www.'):
            url_text = f'https://{url_text}'
        elif url_text.lower().startswith('http://') and not url_text.lower().startswith('http://www.'):
            url_text = url_text.replace('http://', 'https://')

        view.load(QUrl(url_text))

    def bookmarkswidet(self):
        if self.tree_view.isVisible():
            self.tree_view.hide()
        else:
            # Clear the current items under bookmarks
            self.bookmarks_item.removeRows(0, self.bookmarks_item.rowCount())

            # Load bookmarks
            with open("BrowserFiles/data/bookmarks.txt", "r") as bookmfile:
                for x in bookmfile:
                    item = QStandardItem(x.strip())  # Create a new QStandardItem for each bookmark
                    self.bookmarks_item.appendRow(item)

            with open("BrowserFiles/data/history.txt", "r") as historyfile:
                for x in historyfile:
                    item = QStandardItem(x.strip())  # Create a new QStandardItem for each bookmark
                    self.history_item.appendRow(item)

            # Calculate the position for the tree_view
            right_edge = self.geometry().width()  # Right edge of the main window
            titlebar_height = self.tab_widget.tabBar().height()  # Assuming the title bar is the height of the tab bar

            # Adjust for the width of the tree_view to align it to the right
            tree_view_x = right_edge - self.tree_view.geometry().width()

            # Move the tree_view to the calculated position
            self.tree_view.move(tree_view_x, titlebar_height)

            self.tree_view.show()

    def on_item_double_clicked(self, index):
        # Get the QStandardItem from the QModelIndex
        item = self.tree_model.itemFromIndex(index)

        # Get the URL from the clicked item
        url = item.text()

        # Load the URL in the current tab
        self.current_tab_load_url_from_item(url)

    def current_tab_load_url_from_item(self, url_text):
        view = self.current_view()
        url_input = self.current_url_input()

        if not url_text.lower().startswith(('http://', 'https://', 'www.')):
            url_text = f'https://www.{url_text}'
        elif url_text.lower().startswith('www.'):
            url_text = f'https://{url_text}'
        elif url_text.lower().startswith('http://') and not url_text.lower().startswith('http://www.'):
            url_text = url_text.replace('http://', 'https://')

        # Set the URL in the URL input field
        url_input.setText(url_text)

        # Load the URL in the browser view
        view.load(QUrl(url_text))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    qtmodern.styles.dark(app)  # Apply the qtmodern dark style

    main_widget = MainWindow()
    # Wrap the main widget in a qtmodern window
    main_widget.show()
    sys.exit(app.exec_())

