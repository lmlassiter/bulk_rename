# -*- coding: utf-8 -*-
# bulk_rename/views.py

"""This module provides the Bulk Renamer main window."""

from collections import deque
from pathlib import Path

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QFileDialog, QWidget

from .rename import Renamer
from .ui.window import Ui_BulkRenamer

FILTERS = ";;".join(
    (
        "PNG Files (*.png)",
        "JPEG Files (*.jpeg)",
        "JPG Files (*.jpg)",
        "GIF Files (*.gif)",
        "Text Files (*.txt)",
        "Python Files (*.py)",
        "MP4 Files (*.mp4)",
    )
)


class Window(QWidget, Ui_BulkRenamer):
    def __init__(self):
        super().__init__()
        self._files = deque()
        self._filesCount = len(self._files)
        self._setupUI()
        self._connectSignalsSlots()

    def _setupUI(self):
        self.setupUi(self)

    def _connectSignalsSlots(self):
        self.loadBtn.clicked.connect(self.loadFiles)
        self.renameBtn.clicked.connect(self.renameFiles)

    def loadFiles(self):
        self.newFileList.clear()
        if self.dirEdit.text():
            initDir = self.dirEdit.text()
        else:
            initDir = str(Path.home())
        files, filter = QFileDialog.getOpenFileNames(
            self, "Choose Files to Rename", initDir, filter=FILTERS
        )
        if len(files) > 0:
            fileExtension = filter[filter.index("*"): -1]
            self.extensionLabel.setText(fileExtension)
            srcDirName = str(Path(files[0]).parent)
            self.dirEdit.setText(srcDirName)
            for file in files:
                self._files.append(Path(file))
                self.srcFileList.addItem(file)
            self._filesCount = len(self._files)

    def renameFiles(self):
            self._runRenamerThread()


    def _runRenamerThread(self):
            prefix = self.renameLn.text()
            self._thread = QThread()
            self._renamer = Renamer(
                files=tuple(self._files),
                prefix=prefix,
            )
            self._renamer.moveToThread(self._thread)
            # Rename
            self._thread.started.connect(self._renamer.renameFiles)
            # Update state
            self._renamer.renamedFile.connect(self._updateStateWhenFileRenamed)
            self._renamer.progressed.connect(self._updateProgressBar)
            # Clean up
            self._renamer.finished.connect(self._thread.quit)
            self._renamer.finished.connect(self._renamer.deleteLater)
            self._thread.finished.connect(self._thread.deleteLater)
            # Run the thread
            self._thread.start()

    def _updateStateWhenFileRenamed(self, newFile):
            self._files.popleft()
            self.srcFileList.takeItem(0)
            self.newFileList.addItem(str(newFile))
    def _updateProgressBar(self, fileNumber):
        progressPercent = int(fileNumber / self._filesCount * 100)
        self.progressBar.setValue(progressPercent)
