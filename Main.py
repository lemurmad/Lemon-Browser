from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
import threading
import requests

import time
import math
import sys
import os


# Variables

ProjectDirectory = "https://raw.githubusercontent.com/lemurmad/Lemon-Browser/"
ImageDirectory = f"{ProjectDirectory}Images/"
StyleSheetDirectory = f"{ProjectDirectory}main/style.qss"


# Functions


def GetImage(ImageName, Raw=False):
    Image = QImage()
    Image.loadFromData(requests.get(f"{ImageDirectory}{ImageName}").content)
    Image = QPixmap(Image)
    if not Raw:
        return QIcon(Image)
    return Image


# Classes


class NewTab:
    def __init__(self, Main, Address=None):
        super(NewTab, self).__init__()
        if Address is None:
            Address = QUrl("https://www.google.com")

        self.MainSelf = Main
        self.Browser = QWebEngineView()
        self.Browser.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        self.Browser.page().fullScreenRequested.connect(lambda request: self.RequestFullscreen(request))
        self.Browser.setUrl(Address)
        self.TabIndex = self.MainSelf.Tabs.addTab(self.Browser, "")
        self.MainSelf.Tabs.setCurrentIndex(self.TabIndex)
        self.MainSelf.WebTabs[self.TabIndex] = self

        self.Browser.urlChanged.connect(lambda Address: self.AddressChanged(Address))
        self.Browser.titleChanged.connect(lambda: self.TitleChange())
        self.Browser.loadFinished.connect(lambda: self.TitleChange())

    def RequestFullscreen(self, Request):
        Fullscreen = Request.toggleOn()
        self.MainSelf.Tabs.setTabsClosable(not Fullscreen)
        self.MainSelf.NavigationBar.setVisible(not Fullscreen)
        if Fullscreen:
            self.MainSelf.Tabs.setStyleSheet("QTabBar::tab {height: 0; width: 0; padding: 0; min-width: 0}")
        else:
            self.MainSelf.Tabs.setStyleSheet(self.MainSelf.DefaultTabStyleSheet)
        return Request.accept()

    def AddressChanged(self, Address):
        self.MainSelf.UpdateAddressBar(Address, self.Browser)

    def TitleChange(self):
        self.MainSelf.Tabs.setTabText(self.TabIndex, self.Browser.page().title())
        self.Browser.disconnect()


class Main(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Main, self).__init__(*args, **kwargs)
        self.setStyleSheet(requests.get(StyleSheetDirectory).text)
        self.Tabs = QTabWidget()
        self.Tabs.setDocumentMode(True)
        self.Tabs.tabBarDoubleClicked.connect(self.OpenTabDoubleClick)
        self.Tabs.currentChanged.connect(self.CurrentTabChanged)
        self.Tabs.setTabsClosable(True)
        self.Tabs.tabCloseRequested.connect(self.CloseCurrentTab)
        self.DefaultTabStyleSheet = self.Tabs.styleSheet()

        self.setCentralWidget(self.Tabs)

        self.NavigationBar = QToolBar("Navigation")
        self.NavigationBar.setIconSize(QSize(18, 18))
        self.addToolBar(self.NavigationBar)

        self.LoadNavigationBar()
        self.WebTabs = {}

        NewTab(self, QUrl("https://www.google.com"))

        self.show()

        self.setWindowIcon(GetImage("Icon.png"))
        self.setWindowTitle("Lemon Browser")

    def UpdateSheet(self):
        F = open(r"c:\Users\lemur\Downloads\style.qss")
        Sheet = F.read()
        F.close()
        self.Sself.setStyleSheet(Sheet)

    def StyleUpdater(self):
        while True:
            time.sleep(1)
            self.Binder.emit()

    def LoadNavigationBar(self):
        self.BackButton = QAction(GetImage("BackArrow.png"), "Back", self)
        self.BackButton.setStatusTip("Back")
        self.BackButton.triggered.connect(lambda: self.Tabs.currentWidget().back())

        self.ForwardButton = QAction(GetImage("ForwardArrow.png"), "Forward", self)
        self.ForwardButton.setStatusTip("Forward")
        self.ForwardButton.triggered.connect(lambda: self.Tabs.currentWidget().forward())

        self.ReloadButton = QAction(GetImage("Reload.png"), "Reload", self)
        self.ReloadButton.setStatusTip("Reload")
        self.ReloadButton.triggered.connect(lambda: self.Tabs.currentWidget().reload())

        self.HomeButton = QAction(GetImage("Home.png"), "Home", self)
        self.HomeButton.setStatusTip("Homepage")
        self.HomeButton.triggered.connect(lambda: self.NavigateAddress(True))

        self.NewTabButton = QAction(GetImage("NewTab.png"), "New Tab", self)
        self.NewTabButton.setStatusTip("New Tab")
        self.NewTabButton.triggered.connect(lambda: NewTab(self))

        self.AddressBar = QLineEdit()
        self.AddressBar.returnPressed.connect(self.NavigateAddress)

        self.NavigationBar.setMovable(False)
        self.NavigationBar.addAction(self.BackButton)
        self.NavigationBar.addAction(self.ForwardButton)
        self.NavigationBar.addAction(self.ReloadButton)
        self.NavigationBar.addAction(self.HomeButton)
        self.NavigationBar.addAction(self.NewTabButton)
        self.NavigationBar.addWidget(self.AddressBar)

    def OpenTabDoubleClick(self, Index):
        if Index == -1:
            pass
            NewTab(self)

    def CurrentTabChanged(self):
        Address = self.Tabs.currentWidget().url()
        self.UpdateAddressBar(Address, self.Tabs.currentWidget())

    def CloseCurrentTab(self, Index):
        if self.Tabs.count() < 2:
            return
        self.WebTabs[Index].Browser.destroy()
        self.Tabs.removeTab(Index)

    def NavigateAddress(self, Default=False):
        Address = QUrl(self.AddressBar.text())
        if Address.scheme() == "":
            SearchFor = Address.toString()
            Address.clear()
            Address.setUrl(f"http://www.google.com/search?q={SearchFor}")
        if Default:
            Address = QUrl("https://www.google.com")
        self.Tabs.currentWidget().setUrl(Address)

    def UpdateAddressBar(self, Address, Browser):
        if Browser != self.Tabs.currentWidget():
            return
        self.AddressBar.setText(Address.toString())
        self.AddressBar.setCursorPosition(0)


app = QApplication(sys.argv)
app.setApplicationName("Lemon Browser")
app.setOrganizationName("Lemon")
app.setOrganizationDomain("Go Commit Toaster Bath.org")
frm = QFrame()

window = Main()#  MainWindow()
window.statusBar().hide()

WindowResolution = [1280, 720]
ScreenResolution = [0, 0]
SRPQ = window.screen().availableSize()
ScreenResolution = [int(SRPQ.width()), int(SRPQ.height())]
ScreenResolution = [int(ScreenResolution[0] / 2) - int(WindowResolution[0] / 2),
                    int(ScreenResolution[1] / 2) - int(WindowResolution[1] / 2)]

window.setGeometry(ScreenResolution[0], ScreenResolution[1], WindowResolution[0], WindowResolution[1])

app.exec_()
