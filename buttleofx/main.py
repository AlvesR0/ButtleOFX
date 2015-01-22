import os
import sys
import numpy
import signal
import logging
import argparse

from pyTuttle import tuttle

from quickmamba.utils import instantcoding

from buttleofx.data import Finder
from buttleofx.gui.viewer import TimerPlayer
from buttleofx.data import ButtleDataSingleton
from buttleofx.event import ButtleEventSingleton
from buttleofx.manager import ButtleManagerSingleton
from buttleofx.core.undo_redo.manageTools import CommandManager
from buttleofx.gui.browser import FileModelBrowser, FileModelBrowserSingleton

from PyQt5 import QtCore, QtGui, QtQml, QtQuick, QtWidgets

# PyCheck
# import pychecker.checker

# Fix throw to display our info
# From the lowest to the highest level : DEBUG - INFO - WARNING - ERROR - CRITICAL (default = WARNING)
# To use it:
# logging.debug("debug message")
# logging.info("info message")
# logging.warning("warning message")
# logging.error("error message")
# logging.critical("critical message")

DEV_MODE = os.environ.get("BUTTLEOFX_DEV", False)

if DEV_MODE:
    # Print in console
    logging.basicConfig(format='Buttle - %(levelname)s - %(message)s', level=logging.DEBUG)
else:
    # Print in a file
    logging.basicConfig(format='Buttle - %(levelname)s - %(asctime)-15s - %(message)s',
                        filename='console.log', filemode='w', level=logging.DEBUG)

# For glViewport
tuttleofx_installed = False
try:
    import pyTuttle  # noqa
    tuttleofx_installed = True
    logging.debug('Use TuttleOFX.')
except:
    logging.debug('TuttleFX not installed, use Python Image Library instead.')

if tuttleofx_installed:
    from buttleofx.gui.viewerGL.glviewport_tuttleofx import GLViewport_tuttleofx as GLViewportImpl
else:
    from buttleofx.gui.viewerGL.glviewport_pil import GLViewport_pil as GLViewportImpl


osname = os.name.lower()
sysplatform = sys.platform.lower()
windows = osname == "nt" and sysplatform.startswith("win")
macos = sysplatform.startswith("darwin")
linux = not windows and not macos
unix = not windows

# Path of this file
currentFilePath = os.path.dirname(os.path.abspath(__file__))
if windows:
    currentFilePath = currentFilePath.replace("\\", "/")

# Make sure that SIGINTs actually stop the application event loop (Qt sometimes
# swallows KeyboardInterrupt exceptions):
signal.signal(signal.SIGINT, signal.SIG_DFL)


class EventFilter(QtCore.QObject):
    def __init__(self, app, engine):
        self.mainApp = app
        self.mainEngine = engine
        self.buttleData = ButtleDataSingleton().get()
        super(EventFilter, self).__init__()

    def onSaveDialogButtonClicked(self, fileToSave):
        self.buttleData.urlOfFileToSave = fileToSave
        self.buttleData.saveData(QtCore.QUrl(self.buttleData.urlOfFileToSave))
        QtCore.QCoreApplication.quit()

    def onExitDialogDiscardButtonClicked(self):
        QtCore.QCoreApplication.quit()

    def onExitDialogSaveButtonClicked(self):
        if self.buttleData.urlOfFileToSave:
            self.buttleData.saveData(self.buttleData.urlOfFileToSave)
            QtCore.QCoreApplication.quit()
        else:
            saveDialogComponent = QtQml.QQmlComponent(self.mainEngine)
            saveDialogComponent.loadUrl(QtCore.QUrl("ButtleOFX/buttleofx/gui/dialogs/FileViewerDialog.qml"))

            saveDialog = saveDialogComponent.create()
            QtQml.QQmlProperty.write(saveDialog, "title", "Save the graph")
            QtQml.QQmlProperty.write(saveDialog, "buttonText", "Save")
            QtQml.QQmlProperty.write(saveDialog, "folderModelFolder", self.buttleData.getHomeDir())

            saveDialog.buttonClicked.connect(self.onSaveDialogButtonClicked)
            saveDialog.show()

    def eventFilter(self, receiver, event):
        if event.type() == QtCore.QEvent.KeyPress:
            # If Alt F4 event ignored
            if event.modifiers() == QtCore.Qt.AltModifier and event.key() == QtCore.Qt.Key_F4:
                event.ignore()
        if event.type() != QtCore.QEvent.Close:
            return super(EventFilter, self).eventFilter(receiver, event)
        if not isinstance(receiver, QtQuick.QQuickWindow) or not receiver.title() == "ButtleOFX":
            return False
        if not self.buttleData.graphCanBeSaved:
            return False

        exitDialogComponent = QtQml.QQmlComponent(self.mainEngine)
        # Note that we give the path relative to run_buttleofx.sh, because that becomes the PWD when this is run.
        # We also do this for the saveDialogComponent in self.onExitDialogSaveButtonClicked().
        exitDialogComponent.loadUrl(QtCore.QUrl("ButtleOFX/buttleofx/gui/dialogs/ExitDialog.qml"))

        exitDialog = exitDialogComponent.create()
        exitDialog.saveButtonClicked.connect(self.onExitDialogSaveButtonClicked)
        exitDialog.discardButtonClicked.connect(self.onExitDialogDiscardButtonClicked)
        exitDialog.show()        

        # Don't call the parent class, so we don't close the application
        return True


class ButtleApp(QtWidgets.QApplication):
    def __init__(self, argv):
        super(ButtleApp, self).__init__(argv)

#    def notify(self, receiver, event):
#        try:
#            logging.info("QApp notify")
#            return super(ButtleApp, self).notify(receiver, event)
#        except Exception as e:
#            logging.exception("QApp notify exception: " + str(e))
#            import traceback
#            traceback.print_exc()
#            return False


gray_color_table = [QtGui.qRgb(i, i, i) for i in range(256)]


def toQImage(im):
    if im is None:
        return QtGui.QImage()

    if im.dtype == numpy.uint8:
        if len(im.shape) == 2:
            qim = QtGui.QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QtGui.QImage.Format_Indexed8)
            qim.setColorTable(gray_color_table)
            return qim

        elif len(im.shape) == 3:
            if im.shape[2] == 3:
                qim = QtGui.QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QtGui.QImage.Format_RGB888)
                return qim
            elif im.shape[2] == 4:
                qim = QtGui.QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QtGui.QImage.Format_ARGB32)
                return qim

    raise ValueError("toQImage: case not implemented.")

# For debug purposes
count_thumbnail = 0


class ImageProvider(QtQuick.QQuickImageProvider):
    def __init__(self):
        QtQuick.QQuickImageProvider.__init__(self, QtQuick.QQuickImageProvider.Image)
        self.thumbnailCache = tuttle.ThumbnailDiskCache()
        self.thumbnailCache.setRootDir(os.path.join(tuttle.core().getPreferences().getTuttleHomeStr(),
                                                    "thumbnails_cache"))

    def requestImage(self, id, size):
        """
        Compute the image using TuttleOFX
        """
        logging.debug("Tuttle ImageProvider: file='%s'" % id)
        try:
            img = self.thumbnailCache.getThumbnail(id)
            numpyImage = img.getNumpyArray()

            # Convert numpyImage to QImage
            qtImage = toQImage(numpyImage)

            # For debug purposes:
            # global count_thumbnail
            # qtImage.save("/tmp/buttle/thumbnail_{0}.png".format(str(count_thumbnail)))
            # count_thumbnail += 1

            return qtImage.copy(), qtImage.size()

        except Exception as e:
            logging.debug("Tuttle ImageProvider: file='%s' => error: {0}".format(id, str(e)))
            qtImage = QtGui.QImage()
            return qtImage, qtImage.size()


def main(argv, app):

    # Preload Tuttle
    tuttle.core().preload()

    # Give to QML acces to TimerPlayer defined in buttleofx/gui/viewer
    QtQml.qmlRegisterType(TimerPlayer, "TimerPlayer", 1, 0, "TimerPlayer")
    # Give to QML access to FileModelBrowser defined in buttleofx/gui/browser
    QtQml.qmlRegisterType(FileModelBrowser, "ButtleFileModel", 1, 0, "FileModelBrowser")
    # Add new QML type
    QtQml.qmlRegisterType(Finder, "FolderListViewItem", 1, 0, "FolderListView")

    QtQml.qmlRegisterType(GLViewportImpl, "Viewport", 1, 0, "GLViewport")

    # Init undo_redo contexts
    cmdManager = CommandManager()
    cmdManager.setActive()
    cmdManager.clean()

    # Create the QML engine
    engine = QtQml.QQmlEngine(app)
    engine.quit.connect(app.quit)
    engine.addImageProvider("buttleofx", ImageProvider())

    # Data
    buttleData = ButtleDataSingleton().get().init(engine, currentFilePath)
    # Manager
    buttleManager = ButtleManagerSingleton().get().init()
    # Event
    buttleEvent = ButtleEventSingleton().get()
    # fileModelBrowser
    browser = FileModelBrowserSingleton().get()

    parser = argparse.ArgumentParser(description=('A command line to execute ButtleOFX, an opensource compositing '
                                                  'software. If you pass a folder as an argument, ButtleOFX will '
                                                  'start at this path.'))
    parser.add_argument('folder', nargs='?', help='Folder to browse')
    args = parser.parse_args()

    if args.folder:
        inputFolder = os.path.abspath(args.folder)
        browser.setFirstFolder(inputFolder)
    else:
        inputFolder = os.path.expanduser("~")
        browser.setFirstFolder(inputFolder)

    # Expose data to QML
    rc = engine.rootContext()
    rc.setContextProperty("_buttleApp", app)
    rc.setContextProperty("_buttleData", buttleData)
    rc.setContextProperty("_buttleManager", buttleManager)
    rc.setContextProperty("_buttleEvent", buttleEvent)
    rc.setContextProperty("_browser", browser)

    iconPath = os.path.join(currentFilePath, "../blackMosquito.png")
    # iconPath = QtCore.QUrl("file:///" + iconPath)
    app.setWindowIcon(QtGui.QIcon(iconPath))

    mainFilepath = os.path.join(currentFilePath, "MainWindow.qml")
    if windows:
        mainFilepath = mainFilepath.replace('\\', '/')

    component = QtQml.QQmlComponent(engine)
    qmlFile = QtCore.QUrl("file:///" + mainFilepath)
    component.loadUrl(qmlFile)
    topLevelItem = component.create()
    # engine.load(QtCore.QUrl("file:///" + mainFilepath))
    # topLevelItem = engine.rootObjects()[0]

    if not topLevelItem:
        print("Errors:")

        for error in component.errors():
            print(error.toString())
            return -1
    topLevelItem.setIcon(QtGui.QIcon(iconPath))

    if DEV_MODE:
        # Declare we are using instant coding tool on this view
        qic = instantcoding.QmlInstantCoding(
            engine,
            instantcoding.ReloadComponent(qmlFile, component, topLevelItem),
            verbose=True)
        # qic = instantcoding.QmlInstantCoding(engine, instantcoding.AskQmlItemToReload(topLevelItem), verbose=True)

        # Add any source file (.qml and .js by default) in current working directory
        parentDir = os.path.dirname(currentFilePath)
        print("Watch directory:", parentDir)
        qic.addFilesFromDirectory(parentDir, recursive=True)

    aFilter = EventFilter(app, engine)
    app.installEventFilter(aFilter)

    topLevelItem.show()
    sys.exit(app.exec_())
