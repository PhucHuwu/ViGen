import asyncio
import logging
import json
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPlainTextEdit,
                             QLineEdit, QPushButton, QLabel,
                             QFileDialog, QHBoxLayout, QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt
from pipelines.script2video_pipeline import Script2VideoPipeline
from pipelines.idea2video_pipeline import Idea2VideoPipeline
from qasync import asyncSlot
from interfaces import CharacterInScene


class Script2VideoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Inputs Group
        self.add_file_picker(layout, "File Script JSON (*):", "path_script")
        self.add_file_picker(layout, "File Characters JSON (Tùy chọn):", "path_chars")
        self.add_file_picker(layout, "File Portrait Registry JSON (Tùy chọn):", "path_registry")

        layout.addWidget(QLabel("Yêu cầu (Requirement):"))
        self.txt_requirement = QPlainTextEdit()
        layout.addWidget(self.txt_requirement)

        layout.addWidget(QLabel("Phong cách (Style):"))
        self.txt_style = QLineEdit("Realistic, cinematographic")
        layout.addWidget(self.txt_style)

        self.btn_run = QPushButton("Chạy (Generate Video)")
        self.btn_run.setStyleSheet("background-color: #00796b; font-weight: bold; padding: 10px;")
        self.btn_run.clicked.connect(self.run_pipeline)
        layout.addWidget(self.btn_run)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.lbl_result = QLabel("")
        self.lbl_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_result.setWordWrap(True)
        layout.addWidget(self.lbl_result)

        layout.addStretch()

    def add_file_picker(self, layout, label, attr_name):
        layout.addWidget(QLabel(label))
        hbox = QHBoxLayout()
        txt = QLineEdit()
        setattr(self, attr_name, txt)
        hbox.addWidget(txt)
        btn = QPushButton("Chọn File")
        btn.clicked.connect(lambda: self.browse_file(txt))
        hbox.addWidget(btn)
        layout.addLayout(hbox)

    def browse_file(self, line_edit):
        fname, _ = QFileDialog.getOpenFileName(self, "Chọn File", "", "JSON Files (*.json);;All Files (*)")
        if fname:
            line_edit.setText(fname)

    @asyncSlot()
    async def run_pipeline(self):
        script_path = self.path_script.text()
        char_path = self.path_chars.text()
        reg_path = self.path_registry.text()

        if not script_path or not os.path.exists(script_path):
            QMessageBox.warning(self, "Thiếu file", "Vui lòng chọn file Script hợp lệ!")
            return

        self.btn_run.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        try:
            # Load Data
            logging.info(f"Loading script from {script_path}")
            with open(script_path, 'r', encoding='utf-8') as f:
                script_data = json.load(f)

            characters = []
            if char_path and os.path.exists(char_path):
                logging.info(f"Loading characters from {char_path}")
                with open(char_path, 'r', encoding='utf-8') as f:
                    chars_data = json.load(f)
                    try:
                        characters = [CharacterInScene.model_validate(c) for c in chars_data]
                    except:
                        # Fallback for list of dicts if model_validate fails or structure differs
                        characters = chars_data

            registry = {}
            if reg_path and os.path.exists(reg_path):
                logging.info(f"Loading registry from {reg_path}")
                with open(reg_path, 'r', encoding='utf-8') as f:
                    registry = json.load(f)

            # Init Pipeline Components
            logging.info("Initializing Pipeline Components from configs/script2video.yaml...")
            pipeline = Idea2VideoPipeline.init_from_config(config_path="configs/script2video.yaml")

            # Prepare Working Dir
            working_dir = os.path.join(pipeline.working_dir, "manual_run")
            os.makedirs(working_dir, exist_ok=True)

            scripts_to_run = script_data if isinstance(script_data, list) else [script_data]
            all_video_paths = []

            total = len(scripts_to_run)
            self.progress_bar.setRange(0, total)

            for i, script_content in enumerate(scripts_to_run):
                self.progress_bar.setValue(i)

                # Check formatting
                if isinstance(script_content, dict):
                    script_content_str = json.dumps(script_content, ensure_ascii=False)
                elif isinstance(script_content, str):
                    script_content_str = script_content
                else:
                    script_content_str = str(script_content)

                scene_dir = os.path.join(working_dir, f"scene_{i}")
                os.makedirs(scene_dir, exist_ok=True)

                s2v = Script2VideoPipeline(
                    chat_model=pipeline.chat_model,
                    image_generator=pipeline.image_generator,
                    video_generator=pipeline.video_generator,
                    working_dir=scene_dir
                )

                vid_path = await s2v(
                    script=script_content_str,
                    user_requirement=self.txt_requirement.toPlainText(),
                    style=self.txt_style.text(),
                    characters=characters,
                    character_portraits_registry=registry
                )
                all_video_paths.append(vid_path)

            self.progress_bar.setValue(total)

            msg = "Videos generated:\n" + "\n".join(all_video_paths)
            self.lbl_result.setText(msg)
            QMessageBox.information(self, "Thành công", f"Đã tạo xong {len(all_video_paths)} video!")

        except Exception as e:
            logging.error(f"Error: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Lỗi", f"Có lỗi xảy ra: {str(e)}")
        finally:
            self.btn_run.setEnabled(True)
            self.progress_bar.setVisible(False)
