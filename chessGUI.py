import threading
import time
from PyQt5 import Qt
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QWidget, QPushButton, QProgressBar, QCheckBox, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog
from BrowserFiles.browserPlugins.chessFiles import chessFuncs


class ChessMainGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.chessCheat = chessFuncs.chessCheat(image_path="image.png")  # Instantiate the chessCheat object
        self.initUI()
     #   self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def initUI(self):
        # Create the buttons
        self.pixmapimg = QPixmap(400, 400)
        self.scanBtn = QPushButton('Scan')
        self.presetupbtn = QPushButton('Pre-Setup')
        self.selectareabutton = QPushButton('Select Area')

        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.bandw = QCheckBox("B/W")
        self.cheatboxauto = QCheckBox("Auto")
        self.cheatbox = QCheckBox("Cheat")

        self.pixmapLabel = QLabel()

        # Create the layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.pixmapLabel)
        layout.addStretch(1)  # Add stretchable space to push the image to the middle

        # Add the buttons to a horizontal layout
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.bandw)
        buttonLayout.addWidget(self.cheatbox)
        buttonLayout.addWidget(self.cheatboxauto)
        buttonLayout.addWidget(self.scanBtn)
        buttonLayout.addWidget(self.presetupbtn)
        buttonLayout.addWidget(self.selectareabutton)
        layout.addLayout(buttonLayout)

        layout.addWidget(self.progressBar)  # Add the progress bar below the buttons

        self.setLayout(layout)
        self.setWindowTitle('Chess UI')

        # Connect the button clicked signal to the function
        self.presetupbtn.clicked.connect(lambda: self.chessCheat.setupimgs(
            QFileDialog.getOpenFileName(self, "Select a PNG file", "", "PNG Files (*.png)")[0]))
        self.scanBtn.clicked.connect(self.updateBoard)
        self.cheatboxauto.clicked.connect(self.startclsthread)
        self.selectareabutton.clicked.connect(self.selboardarea)

    def scansrn(self):
        while self.cheatboxauto.isChecked():
            screenchanged = self.chessCheat.detect_screen_change(self.chessCheat.croploc[0], 'on')

            if screenchanged:
                time.sleep(4)
                self.updateBoard()

    def startclsthread(self):
        if self.cheatboxauto:
            screen_monitor_thread = threading.Thread(target=self.scansrn)
            screen_monitor_thread.daemon = True  # Set the thread as a daemon thread
            screen_monitor_thread.start()

    def selboardarea(self):
        print(self.chessCheat.croploc)
        self.chessCheat.croploc = self.chessCheat.scanBoard()

    def presetup(self):
        self.chessCheat.setupimgs()

    def updateBoard(self):

        try:
            if self.bandw.isChecked():
                self.chessCheat.side_to_move = "b"

            else:
                self.chessCheat.side_to_move = "w"

            if self.cheatbox.isChecked():

                bestmov, evl = self.chessCheat.updateboard(cheat='on')
            else:
                bestmov, evl = self.chessCheat.updateboard()

            ev = max(0, min(100, int(evl['value'] / 50 + 50)))
            self.progressBar.setValue(ev)
            print(bestmov, ev)

            # Update the progress bar value
            # self.progressBar.setValue(normalized_score)
            svgRenderer = QSvgRenderer()
            svgRenderer.load(f"chess/curboard.svg")

            # Paint the SVG image onto the QPixmap
            self.pixmapimg.fill(Qt.transparent)  # Set the QPixmap background to transparent
            painter = QPainter(self.pixmapimg)
            svgRenderer.render(painter)
            painter.end()
            self.pixmapLabel.setPixmap(self.pixmapimg)

        except Exception as e:
            # Handle any exceptions that may occur during the update process
            print(f"Error updating the board: {str(e)}")
