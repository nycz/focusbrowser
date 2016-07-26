#!/usr/bin/env python3
import os
from os.path import join
import pickle
import re
import subprocess
import sys

from PyQt4 import QtGui, QtCore, QtWebKit, QtNetwork
from PyQt4.QtCore import Qt, QUrl

from libsyntyche.common import read_json, kill_theming, local_path, make_sure_config_exists


class CookieJar(QtNetwork.QNetworkCookieJar):
    def __init__(self, cookiepath):
        super().__init__()
        self.cookiepath = cookiepath
        self.load_cookies()

    def load_cookies(self):
        try:
            with open(self.cookiepath, 'rb') as f:
                cookiedata = pickle.load(f)
        except FileNotFoundError:
            pass
        else:
            cookies = [c for rawcookies in cookiedata
                       for c in QtNetwork.QNetworkCookie.parseCookies(rawcookies)]
            self.setAllCookies(cookies)

    def save_cookies(self):
        cookiedata = [c.toRawForm() for c in self.allCookies()]
        with open(self.cookiepath, 'wb') as f:
            pickle.dump(cookiedata, f)


class WebView(QtWebKit.QWebView):

    def __init__(self, parent, whitelist):
        super().__init__(parent)
        self.settings().setUserStyleSheetUrl(QUrl('file://' + local_path('styleoverride.css')))
        self.whitelist = whitelist

    def valid_url(self, qurl):
        url = qurl.toString()
        for rx in self.whitelist:
            if re.fullmatch(rx, url):
                return True
        return False

    def mousePressEvent(self, ev):
        if ev.button() == Qt.RightButton:
            ev.ignore()
            return
        if ev.button() == Qt.XButton1:
            self.back()
        elif ev.button() == Qt.XButton2:
            self.forward()
        else:
            hittest = self.page().currentFrame().hitTestContent(ev.pos())
            if hittest.isNull():
                ev.ignore()
                return
            url = hittest.linkUrl()
            if self.valid_url(url):
                if ev.button() == Qt.MiddleButton:
                    subprocess.Popen([sys.executable, sys.argv[0], url.toString()])
                elif ev.button() == Qt.LeftButton:
                    self.load(url)
        ev.accept()



class MainWindow(QtGui.QWidget):
    def __init__(self, url):
        super().__init__()
        self.setWindowTitle('focusbrowser')
        self.configdir = join(os.getenv('HOME'), '.config', 'focusbrowser')

        self.settings = read_config(self.configdir)

        self.cookiejar = CookieJar(join(self.configdir, 'cookies.pickle'))

        layout = QtGui.QVBoxLayout(self)
        kill_theming(layout)
        self.view = WebView(self, self.settings['whitelist regexes'])
        self.view.page().networkAccessManager().setCookieJar(self.cookiejar)
        layout.addWidget(self.view)
        if url:
            self.view.load(QUrl(url))
        else:
            self.view.load(QUrl(self.settings['default url']))
        self.show()


    def closeEvent(self, ev):
        self.cookiejar.save_cookies()
        ev.accept()

def read_config(configdir):
    configpath = join(configdir, 'settings.json')
    make_sure_config_exists(configpath, local_path('defaultconfig.json'))
    return read_json(configpath)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('url', nargs='?')
    args = parser.parse_args()

    app = QtGui.QApplication(sys.argv)

    window = MainWindow(args.url)
    app.setActiveWindow(window)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
