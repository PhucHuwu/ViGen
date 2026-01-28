import yaml
import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit,
                             QPushButton, QGroupBox, QMessageBox, QComboBox, QLabel)


class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.configs = {
            "Idea2Video Config": "configs/idea2video.yaml",
            "Script2Video Config": "configs/script2video.yaml"
        }
        self.current_config_key = "Idea2Video Config"
        self.config_data = {}

        self.init_ui()
        self.load_current_config()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Config Selector
        layout.addWidget(QLabel("Chọn file cấu hình cần sửa:"))
        self.combo_config = QComboBox()
        self.combo_config.addItems(list(self.configs.keys()))
        self.combo_config.currentTextChanged.connect(self.on_config_changed)
        layout.addWidget(self.combo_config)

        # OpenRouter / Chat Model Section
        group_chat = QGroupBox("Cấu hình Chat Model (OpenRouter)")
        form_chat = QFormLayout()

        self.input_chat_model = QLineEdit()
        self.input_chat_api_key = QLineEdit()
        self.input_chat_base_url = QLineEdit()

        form_chat.addRow("Model Name:", self.input_chat_model)
        form_chat.addRow("API Key:", self.input_chat_api_key)
        form_chat.addRow("Base URL:", self.input_chat_base_url)
        group_chat.setLayout(form_chat)
        layout.addWidget(group_chat)

        # Google GenAI Section (Image/Video)
        group_google = QGroupBox("Cấu hình Google GenAI (Image/Video)")
        form_google = QFormLayout()

        self.input_google_api_key = QLineEdit()
        self.input_image_rpm = QLineEdit()
        self.input_video_rpm = QLineEdit()

        form_google.addRow("Google API Key:", self.input_google_api_key)
        form_google.addRow("Image Limit (RPM):", self.input_image_rpm)
        form_google.addRow("Video Limit (RPM):", self.input_video_rpm)

        group_google.setLayout(form_google)
        layout.addWidget(group_google)

        # Save Button
        btn_save = QPushButton("Lưu cấu hình")
        btn_save.clicked.connect(self.save_config)
        layout.addWidget(btn_save)

        layout.addStretch()

    def on_config_changed(self, text):
        self.current_config_key = text
        self.load_current_config()

    def load_current_config(self):
        path = self.configs[self.current_config_key]
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f)

            # Chat Model
            chat_args = self.config_data.get('chat_model', {}).get('init_args', {})
            self.input_chat_model.setText(str(chat_args.get('model', '')))
            self.input_chat_api_key.setText(str(chat_args.get('api_key', '')))
            self.input_chat_base_url.setText(str(chat_args.get('base_url', '')))

            # Google GenAI
            # Assuming shared key or first available
            img_args = self.config_data.get('image_generator', {}).get('init_args', {})
            vid_args = self.config_data.get('video_generator', {}).get('init_args', {})

            # Prefer image key, fallback to video key
            google_key = img_args.get('api_key') or vid_args.get('api_key') or ''
            self.input_google_api_key.setText(str(google_key))

            # Limits
            img_rpm = self.config_data.get('image_generator', {}).get('max_requests_per_minute', '')
            vid_rpm = self.config_data.get('video_generator', {}).get('max_requests_per_minute', '')
            self.input_image_rpm.setText(str(img_rpm) if img_rpm is not None else '')
            self.input_video_rpm.setText(str(vid_rpm) if vid_rpm is not None else '')

            logging.info(f"Loaded config from {path}")

        except Exception as e:
            logging.error(f"Failed to load config {path}: {e}")
            self.input_chat_model.clear()
            # Don't show critical popup on load fail if file just empty/missing, but log it.

    def save_config(self):
        path = self.configs[self.current_config_key]
        try:
            # Update data structure
            if 'chat_model' not in self.config_data:
                self.config_data['chat_model'] = {'init_args': {}}

            self.config_data['chat_model']['init_args']['model'] = self.input_chat_model.text()
            self.config_data['chat_model']['init_args']['api_key'] = self.input_chat_api_key.text()
            self.config_data['chat_model']['init_args']['base_url'] = self.input_chat_base_url.text()

            # Image Generator
            if 'image_generator' not in self.config_data:
                self.config_data['image_generator'] = {'init_args': {}}
            self.config_data['image_generator']['init_args']['api_key'] = self.input_google_api_key.text()

            if self.input_image_rpm.text():
                try:
                    self.config_data['image_generator']['max_requests_per_minute'] = int(self.input_image_rpm.text())
                except:
                    pass

            # Video Generator
            if 'video_generator' not in self.config_data:
                self.config_data['video_generator'] = {'init_args': {}}
            self.config_data['video_generator']['init_args']['api_key'] = self.input_google_api_key.text()

            if self.input_video_rpm.text():
                try:
                    self.config_data['video_generator']['max_requests_per_minute'] = int(self.input_video_rpm.text())
                except:
                    pass

            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, allow_unicode=True)

            logging.info(f"Saved config to {path}")
            QMessageBox.information(self, "Thành công", f"Đã lưu cấu hình vào {path}!")

        except Exception as e:
            logging.error(f"Failed to save config: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không lưu được cấu hình: {e}")
