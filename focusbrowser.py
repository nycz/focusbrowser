#!/usr/bin/env python3
import os
from os.path import join
import re
import subprocess
import sys

from PyQt5 import QtWidgets, QtWebEngineWidgets, QtNetwork
from PyQt5.QtCore import Qt, QUrl, QObject, QEvent

from libsyntyche.common import read_json, write_json, local_path, make_sure_config_exists


class WebPage(QtWebEngineWidgets.QWebEnginePage):
    def __init__(self, parent, profile, valid_url):
        super().__init__(profile, parent)
        self.valid_url = valid_url

    def acceptNavigationRequest(self, url, navtype, ismainframe):
        if ismainframe:
            return self.valid_url(url)
        else:
            return True

class WebView(QtWebEngineWidgets.QWebEngineView):

    def __init__(self, parent, whitelist, configdir):
        super().__init__(parent)
        self.whitelist = whitelist
        profile = QtWebEngineWidgets.QWebEngineProfile('Default', self)
        self.setPage(WebPage(self, profile, self.valid_url))

    def valid_url(self, qurl):
        url = qurl.toString()
        for rx in self.whitelist:
            if re.fullmatch(rx, url):
                return True
        return False


class MainWindow(QtWidgets.QWidget):
    def __init__(self, url):
        super().__init__()
        self.setWindowTitle('focusbrowser')
        self.configdir = join(os.getenv('HOME'), '.config', 'focusbrowser')

        self.settings = read_config(self.configdir)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        self.view = WebView(self, self.settings['whitelist regexes'], self.configdir)

        layout.addWidget(self.view)
        if url:
            self.view.load(QUrl(url))
        else:
            self.view.load(QUrl(self.settings['default url']))
        self.show()


def read_config(configdir):
    configpath = join(configdir, 'settings.json')
    make_sure_config_exists(configpath, local_path('defaultconfig.json'))
    return read_json(configpath)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('url', nargs='?')
    args = parser.parse_args()

    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow(args.url)
    app.setActiveWindow(window)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
