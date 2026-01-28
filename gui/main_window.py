from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QSplitter
from PyQt6.QtCore import Qt
from gui.tabs.settings_tab import SettingsTab
from gui.components.log_viewer import LogViewer
from gui.tabs.idea2video_tab import Idea2VideoTab
from gui.tabs.script2video_tab import Script2VideoTab


from PyQt6.QtGui import QIcon
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ViGen - AI Video Generator")
        self.resize(1200, 800)

        # Set Window Icon
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Splitter to separate Loop/Tabs from Logs
        splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(splitter)

        # Tab Widget
        self.tabs = QTabWidget()

        # Idea -> Video Tab
        self.tab_idea = Idea2VideoTab()

        # Script -> Video Tab
        self.tab_script = Script2VideoTab()

        # Settings Tab
        self.tab_settings = SettingsTab()

        self.tabs.addTab(self.tab_idea, "Idea -> Video")
        self.tabs.addTab(self.tab_script, "Script -> Video")
        self.tabs.addTab(self.tab_settings, "Cấu hình (Config)")

        splitter.addWidget(self.tabs)

        # Log Viewer
        self.log_viewer = LogViewer()
        splitter.addWidget(self.log_viewer)

        # Set initial sizes for splitter (70% top, 30% bottom)
        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)
