# -*- coding: utf-8 -*-
#bulk_rename/app.py

"""This provides the Bulk Renamer Application"""

import sys

from PyQt5.QtWidgets import QApplication

from .views import Window

def main():
    # Start app
    app = QApplication(sys.argv)
    # Start and show the window
    win = Window()
    win.show()
    # Run event loop
    sys.exit(app.exec())
