
import logging
from PyQt6.QtWidgets import QPlainTextEdit, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtGui import QFont, QTextCursor


class LogSignal(QObject):
    log_received = pyqtSignal(str)


class QueueHandler(logging.Handler):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def emit(self, record):
        msg = self.format(record)
        self.signal.log_received.emit(msg)


class LogViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.header = QLabel("Nhật ký hoạt động (Logs)")
        self.header.setStyleSheet("font-weight: bold; padding: 5px;")
        self.layout.addWidget(self.header)

        self.text_edit = QPlainTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Consolas", 10))
        self.layout.addWidget(self.text_edit)

        # Setup Logging Handler
        self.log_signal = LogSignal()
        self.log_signal.log_received.connect(self.append_log)

        self.handler = QueueHandler(self.log_signal)
        self.handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(self.handler)
        logging.getLogger().setLevel(logging.INFO)

    def append_log(self, text):
        self.text_edit.moveCursor(QTextCursor.MoveOperation.End)
        self.text_edit.insertPlainText(text + "\n")
        self.text_edit.moveCursor(QTextCursor.MoveOperation.End)
