__author__ = 'Suchakra'

import sys
import os
import rawpy
import imageio
import fnmatch
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

rawr_ui = uic.loadUiType("ui.ui")[0]

class RawrWindowClass(QMainWindow, rawr_ui):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(TITLE)
        self.setWindowIcon(ICON)

        self.fileList = []
        self.fileIndex = 0

        # Stylesheet ~Yasin Uludag (LoneWolf)
        ss="darkorange.stylesheet"
        with open(ss, "r") as fh:
            self.setStyleSheet(fh.read())
        self.imageView.setStyleSheet("background: black; border: 0px")

        # Setup default screen
        self.scene = QGraphicsScene()
        self.imageView.setScene(self.scene)
        self.default_flag = True
        defaultImg = 'splash.png'
        pixMap = QPixmap(defaultImg)
        self.scene.addPixmap(pixMap)
        self.scene.update()
        self.progressBar.setRange(0, 1)
        self.progressBar.setFixedWidth(60)


        # Setup buttons
        self.nextButton.setIcon(NEXT)
        self.backButton.setIcon(BACK)
        self.openButton.setIcon(CAMERA)
        self.openButton.setToolTip('Open RAW image')
        self.saveButton.setIcon(SAVE)
        self.saveButton.setToolTip('Save image as JPEG')

        # Button handlers
        self.actionOpen.triggered.connect(self.openImage)
        self.openButton.clicked.connect(self.openImage)
        self.actionExport.triggered.connect(self.exportImage)
        self.nextButton.clicked.connect(self.nextImage)
        self.backButton.clicked.connect(self.prevImage)
        self.saveButton.clicked.connect(self.saveAsJpeg)

        self.thread = Worker()
        self.connect(self.thread, SIGNAL("finished()"), self.updateUi)
        self.connect(self.thread, SIGNAL("terminated()"), self.updateUi)
        #self.connect(self.thread, SIGNAL("out()"), self.updateUi)

    def startRawProcessThread(self, path):
        self.progressBar.setRange(0, 0)
        if path is not '':
            self.thread.rawProcess(path)
            return True
        else:
            return False

    def updateUi(self):
        self.default_flag = False
        self.scene.clear()
        pixMap = QPixmap('/tmp/img.tiff')
        self.scene.addPixmap(pixMap)
        self.scene.update()
        self.progressBar.setRange(0, 1)

    def nextImage(self):
        self.fileIndex = (self.fileIndex+1) % len(self.fileList)
        path = self.fileList[self.fileIndex]
        self.startRawProcessThread(path)

    def prevImage(self):
        self.fileIndex = (self.fileIndex-1) % len(self.fileList)
        path = self.fileList[self.fileIndex]
        self.startRawProcessThread(path)

    def resizeEvent(self, event):
        if self.default_flag is False:
            self.imageView.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def showEvent(self, event):
        if self.default_flag is False:
            self.imageView.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def saveAsJpeg(self):
        img = imageio.imread('/tmp/img.tiff')
        outName = self.fileList[self.fileIndex]
        outName = os.path.splitext(outName)[0] + '.jpg'
        imageio.imsave(outName, img)

    def openImage(self):
        filename = QFileDialog.getOpenFileName(self, 'Open Image', os.getenv('HOME'))
        filename = str(filename)
        if filename is not '':
            ext = os.path.splitext(filename)[1]
            self.currDir = os.path.dirname(filename)

            for file in os.listdir(self.currDir):
                if fnmatch.fnmatch(file, '*'+ext):
                    newPath = str(self.currDir+'/'+file)
                    self.fileList.append(newPath)
            self.fileIndex = self.fileList.index(newPath)

        self.startRawProcessThread(filename)

    def openDirectory(self):
        return True

    def exportImage(self):
        return True

class Worker(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)

    def __del__(self):
        self.exiting = True
        self.wait()

    def rawProcess(self, path):
        self.path = path
        self.start()

    def run(self):
        raw = rawpy.imread(self.path)
        rgb = raw.postprocess()
        #rgb = QImage(rgb)
        imageio.imsave('/tmp/img.tiff', rgb)
        #self.emit(SIGNAL("out(QImage)"), rgb)

app = QApplication(sys.argv)
TITLE = str("RAW Reader")

# Icons (Font Awesome) ~Dave Gandy
BACK = QIcon('chevron19.png')
NEXT = QIcon('chevron24.png')
CAMERA = QIcon('photo33.png')
SAVE = QIcon('download63.png')
ICON = QIcon('default.png')
myWindow = RawrWindowClass(None)
myWindow.show()
app.exec_()