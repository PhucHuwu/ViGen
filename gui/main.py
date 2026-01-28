import sys
import asyncio
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication
from qasync import QEventLoop
from qt_material import apply_stylesheet
from gui.main_window import MainWindow
import logging


import os


def ensure_configs():
    """Ensure that default config files exist."""
    config_dir = "configs"
    os.makedirs(config_dir, exist_ok=True)

    defaults = {
        "idea2video.yaml": """
chat_model:
    init_args:
        model: "google/gemini-2.0-flash-exp:free"
        model_provider: "openai"
        api_key: "YOUR_OPENROUTER_API_KEY"
        base_url: "https://openrouter.ai/api/v1"
    # Rate limits for chat model API calls
    max_requests_per_minute: 10
    max_requests_per_day: 500

image_generator:
    class_path: "tools.ImageGeneratorNanobananaGoogleAPI"
    init_args:
        api_key: "YOUR_GOOGLE_API_KEY"
    # Rate limits for image generation API calls
    max_requests_per_minute: 10
    max_requests_per_day: 500

video_generator:
    class_path: "tools.VideoGeneratorVeoGoogleAPI"
    init_args:
        api_key: "YOUR_GOOGLE_API_KEY"
    # Rate limits for video generation API calls
    max_requests_per_minute: 2
    max_requests_per_day: 10

working_dir: .working_dir/idea2video
""",
        "script2video.yaml": """
chat_model:
    init_args:
        model: "google/gemini-2.0-flash-exp:free"
        model_provider: "openai"
        api_key: "YOUR_OPENROUTER_API_KEY"
        base_url: "https://openrouter.ai/api/v1"
    # Rate limits for chat model API calls
    max_requests_per_minute: 10
    max_requests_per_day: 500

image_generator:
    class_path: "tools.ImageGeneratorNanobananaGoogleAPI"
    init_args:
        api_key: "YOUR_GOOGLE_API_KEY"
    # Rate limits for image generation API calls
    max_requests_per_minute: 10
    max_requests_per_day: 500

video_generator:
    class_path: "tools.VideoGeneratorVeoGoogleAPI"
    init_args:
        api_key: "YOUR_GOOGLE_API_KEY"
    # Rate limits for video generation API calls
    max_requests_per_minute: 2
    max_requests_per_day: 10

working_dir: .working_dir/script2video
"""
    }

    for filename, content in defaults.items():
        path = os.path.join(config_dir, filename)
        if not os.path.exists(path):
            logging.info(f"Creating default config: {path}")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content.strip())


def main():
    ensure_configs()
    
    # Fix Qt plugin paths for PyInstaller on macOS
    if hasattr(sys, '_MEIPASS'):
        # Running in PyInstaller bundle
        qt_plugin_path = os.path.join(sys._MEIPASS, 'PyQt6', 'Qt6', 'plugins')
        if os.path.exists(qt_plugin_path):
            QCoreApplication.setLibraryPaths([qt_plugin_path])
    
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
