import sys
import asyncio
from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop
from qt_material import apply_stylesheet
from gui.main_window import MainWindow
import logging


def main():
    app = QApplication(sys.argv)

    # Setup Async Loop
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Apply Theme
    # 'dark_teal.xml' is a popular choice, can be changed later
    apply_stylesheet(app, theme='dark_teal.xml')

    window = MainWindow()
    window.show()

    logging.info("ViMax Desktop GUI Started")

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
