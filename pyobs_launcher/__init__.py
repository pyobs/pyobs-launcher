import argparse
import os
import signal
import sys
import subprocess
import threading
import time
from typing import List

import yaml
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication


class ConfigRunner(QtWidgets.QWidget):
    add_to_log = QtCore.pyqtSignal(str)

    def __init__(self, config, python, pyobs, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)

        # store config
        self.config = config
        self.python = python
        self.pyobs = pyobs

        # add layout and text browser
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)
        self.browser = QtWidgets.QTextBrowser(self)
        layout.addWidget(self.browser)

        # connect signal
        self.add_to_log.connect(self.browser.append)

        # start thread
        self.process = None
        self.thread = threading.Thread(target=self._run_thread)
        self.thread.start()

    def terminate(self):
        if self.process is not None:
            # windows or linux?
            if sys.platform == 'win32':
                # on Windows, we send a CTRL-C event, then kill process
                # for whatever reason, but that seems to terminate the process gracefully...
                os.kill(self.process.pid, signal.CTRL_C_EVENT)
                self.process.kill()
            else:
                # on linux, a terminate is good
                self.process.terminate()

            # wait for thread, but keep GUI alive
            waited = 0
            while self.thread.is_alive():
                # keep Qt alive
                QApplication.processEvents()

                # wait a little
                waited += 0.1
                time.sleep(0.1)

                # too long?
                if waited > 10:
                    self.process.kill()
                    waited = 0

    def _run_thread(self):
        # use shell only in windows
        shell = sys.platform == 'win32'

        # define command
        if self.python is None:
            cmd = [self.pyobs]
        else:
            cmd = [self.python, self.pyobs]
        cmd += [os.path.basename(self.config)]

        # start process
        self.process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True,
                                        cwd=os.path.dirname(self.config), shell=shell)

        # read lines until process terminates
        for line in self.process.stderr:
            line = line.strip()
            if len(line) > 0:
                self.add_to_log.emit(line)

        # terminated
        self.process = None


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, pyobs: str = None, python: str = None, configs: List[str] = None, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)

        # store
        self._pyobs_executable = 'pyobs' if pyobs is None else pyobs
        self._python_executable = python
        self._configs = [] if configs is None else configs

        # set title, size, etc
        self.setWindowTitle('pyobs launcher')
        self.resize(800, 600)

        # add tabs
        self.tabs = QtWidgets.QTabWidget(self)
        self.setCentralWidget(self.tabs)

        # load configs
        for filename in self._configs:
            runner = ConfigRunner(filename, self._python_executable, self._pyobs_executable, parent=self)
            self.tabs.addTab(runner, os.path.basename(filename))

    def closeEvent(self, ev: QtGui.QCloseEvent):
        # wait cursor
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        # loop all tabs
        for i in range(self.tabs.count()):
            # get widget and terminate ut
            widget = self.tabs.widget(i)
            widget.terminate()

        # accept event
        ev.accept()


def signal_handler(signal, frame):
    # just need to receive it
    pass


def main():
    # catch signals
    signal.signal(signal.SIGINT, signal_handler)

    # init command line parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Config to load', type=str, default='config.yaml')

    # parse it
    args = parser.parse_args()

    # load config
    with open(args.config) as f:
        cfg = yaml.safe_load(f)

    # create app
    app = QtWidgets.QApplication([])

    # create and show window
    window = MainWindow(**cfg)
    window.show()

    # run
    app.exec()
