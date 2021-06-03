import PyQt5.QtWebEngineWidgets
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
import requests

import time
import math
import sys
import os


def LoadImage(URL, JPM=False):
    ImageLocationURL = "https://raw.githubusercontent.com/lemurmad/Lemon-Browser/Images/"
    ImageQ = QImage()
    ImageQ.loadFromData(requests.get(f"{ImageLocationURL}{URL}").content)
    if not JPM:
        return QIcon(QPixmap(ImageQ))
    return QPixmap(ImageQ)


class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)

        QBtn = QDialogButtonBox.Ok  # No cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()

        title = QLabel("Lemon Browser")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)

        layout.addWidget(title)

        logo = QLabel()
        logo.setPixmap(LoadImage('Help.png', JPM=True)) # ma-icon-128.png
        layout.addWidget(logo)

        layout.addWidget(QLabel("Version 1.0"))
        layout.addWidget(QLabel("Made By Dog :)\nBased on the Mozarella Project\nPowered by chrome"))

        for i in range(0, layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)

        layout.addWidget(self.buttonBox)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        css = requests.get("https://raw.githubusercontent.com/lemurmad/Lemon-Browser/main/style.qss").text
        self.setStyleSheet(css)
        self.tabs = QTabWidget()
        # self.setWindowFlag()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.setCentralWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        navtb = QToolBar("Navigation")
        navtb.setIconSize(QSize(18, 18))
        self.addToolBar(navtb)

        back_btn = QAction(LoadImage("BackArrow.png"), "Back", self)
        back_btn.setStatusTip("Back")
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        navtb.addAction(back_btn)

        next_btn = QAction(LoadImage("ForwardArrow.png"), "Forward", self)
        next_btn.setStatusTip("Forward")
        next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navtb.addAction(next_btn)

        reload_btn = QAction(LoadImage("Reload.png"), "Reload Page", self)
        reload_btn.setStatusTip("Reload")
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navtb.addAction(reload_btn)

        home_btn = QAction(LoadImage("Home.png"), "Home", self)
        home_btn.setStatusTip("Home")
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        ntab_btn = QAction(LoadImage("NewTab.png"), "New Tab", self)
        ntab_btn.setStatusTip("New Tab")
        ntab_btn.triggered.connect(lambda: self.add_new_tab())
        navtb.addAction(ntab_btn)

        navtb.addSeparator()

        self.httpsicon = QLabel()  # Yes, really!
        self.httpsicon.setPixmap(LoadImage("Unsecure.png", JPM=True))
        navtb.addWidget(self.httpsicon)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

        stop_btn = QAction(LoadImage("Stop.png"), "Stop Loading",
                           self)  # QIcon(os.path.join('images', 'cross-circle.png'))
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        navtb.addAction(stop_btn)

        # Uncomment to disable native menubar on Mac
        # self.menuBar().setNativeMenuBar(False)

        file_menu = self.menuBar().addMenu("&File")

        new_tab_action = QAction(LoadImage("NewTab.png"), "New Tab",
                                 self)  # QIcon(os.path.join('images', 'ui-tab--plus.png'))
        new_tab_action.setStatusTip("Open a new tab")
        new_tab_action.triggered.connect(lambda _: self.add_new_tab())
        file_menu.addAction(new_tab_action)

        navtb.setMovable(False)

        open_file_action = QAction(LoadImage('Help.png'), "Open file...", self) # disk--arrow
        open_file_action.setStatusTip("Open from file")
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)

        save_file_action = QAction(LoadImage('Help.png'), "Save Page As...", self) # disk--pencil
        save_file_action.setStatusTip("Save current page to file")
        save_file_action.triggered.connect(self.save_file)
        file_menu.addAction(save_file_action)

        print_action = QAction(LoadImage('Help.png'), "Print...", self) # printer.png
        print_action.setStatusTip("Print current page")
        print_action.triggered.connect(self.print_page)
        file_menu.addAction(print_action)

        help_menu = self.menuBar().addMenu("&Help")

        about_action = QAction(LoadImage('Help.png'), "About Lemon Browser", self)
        about_action.setStatusTip("Find out more about Lemon Browser")  # Hungry!
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)

        navigate_mozarella_action = QAction(LoadImage('Help.png'),
                                            "Lemon Browser Homepage", self)
        navigate_mozarella_action.setStatusTip("Go to Lemon Browser Homepage")
        navigate_mozarella_action.triggered.connect(self.navigate_mozarella)
        help_menu.addAction(navigate_mozarella_action)

        self.add_new_tab(QUrl('https://www.google.com'), 'Homepage')

        self.show()

        self.setWindowTitle("Lemon Browser")
        self.setWindowIcon(LoadImage("Help.png"))

    def add_new_tab(self, qurl=None, label=""):

        if qurl is None:
            qurl = QUrl('https://www.google.com')

        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)

        self.tabs.setCurrentIndex(i)

        # More difficult! We only want to update the url when it's from the
        # correct tab
        browser.urlChanged.connect(lambda qurl, browser=browser:
                                   self.update_urlbar(qurl, browser))

        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabs.setTabText(i, browser.page().title()))

    def tab_open_doubleclick(self, i):
        if i == -1:  # No tab under the click
            pass
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return

        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            # If this signal is not from the current tab, ignore
            return

        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle("%s - Lemon Browser" % title)

    def navigate_mozarella(self):
        self.tabs.currentWidget().setUrl(QUrl("https://www.google.com/"))

    def about(self):
        dlg = AboutDialog()
        dlg.exec_()

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                                  "Hypertext Markup Language (*.htm *.html);;"
                                                  "All files (*.*)")

        if filename:
            with open(filename, 'r') as f:
                html = f.read()

            self.tabs.currentWidget().setHtml(html)
            self.urlbar.setText(filename)

    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Page As", "",
                                                  "Hypertext Markup Language (*.htm *html);;"
                                                  "All files (*.*)")

        if filename:
            html = self.tabs.currentWidget().page().toHtml()
            with open(filename, 'w') as f:
                f.write(html.encode('utf8'))

    def print_page(self):
        return None
        dlg = QPrintPreviewDialog()
        dlg.paintRequested.connect(self.browser.print_)
        dlg.exec_()

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("https://www.google.com/"))

    def navigate_to_url(self):  # Does not receive the Url
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            SearchFor = q.toString()
            q.clear()
            q.setUrl(f"http://www.google.com/search?q={SearchFor}")
        self.tabs.currentWidget().setUrl(q)

    def update_urlbar(self, q, browser=None):

        if browser != self.tabs.currentWidget():
            # If this signal is not from the current tab, ignore
            return

        if q.scheme() == 'https':
            # Secure padlock icon
            self.httpsicon.setPixmap(LoadImage("Secure.png", JPM=True))

        else:
            # Insecure padlock icon
            self.httpsicon.setPixmap(LoadImage("Unsecure.png", JPM=True))

        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)


app = QApplication(sys.argv)
app.setApplicationName("Lemon Browser")
app.setOrganizationName("Lemon")
app.setOrganizationDomain("Go Commit Toaster Bath.org")
frm = QFrame()

window = MainWindow()
window.statusBar().hide()

WindowResolution = [1280, 720]
ScreenResolution = [0, 0]
SRPQ = window.screen().availableSize()
ScreenResolution = [int(SRPQ.width()), int(SRPQ.height())]
ScreenResolution = [int(ScreenResolution[0] / 2) - int(WindowResolution[0] / 2),
                    int(ScreenResolution[1] / 2) - int(WindowResolution[1] / 2)]

window.setGeometry(ScreenResolution[0], ScreenResolution[1], WindowResolution[0], WindowResolution[1])

app.exec_()
