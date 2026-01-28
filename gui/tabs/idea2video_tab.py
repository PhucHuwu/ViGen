import asyncio
import logging
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPlainTextEdit,
                             QLineEdit, QPushButton, QTabWidget, QLabel,
                             QSplitter, QScrollArea, QGridLayout, QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from pipelines.idea2video_pipeline import Idea2VideoPipeline
from qasync import asyncSlot
from moviepy import VideoFileClip, concatenate_videoclips


class Idea2VideoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.pipeline = None
        self.working_dir = None

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left Side: Inputs
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)

        input_layout.addWidget(QLabel("Ý tưởng (Idea):"))
        self.txt_idea = QPlainTextEdit()
        input_layout.addWidget(self.txt_idea)

        input_layout.addWidget(QLabel("Yêu cầu (Requirement):"))
        self.txt_requirement = QPlainTextEdit()
        input_layout.addWidget(self.txt_requirement)

        input_layout.addWidget(QLabel("Phong cách (Style):"))
        self.txt_style = QLineEdit("Realistic, warm feel")
        input_layout.addWidget(self.txt_style)

        self.btn_run = QPushButton("Chạy (Generate Video)")
        self.btn_run.setProperty("class", "cta")  # CTA for main action
        self.btn_run.clicked.connect(self.run_pipeline)

        self.btn_clear = QPushButton("Xóa Cache (Reset)")
        self.btn_clear.setProperty("class", "danger")  # Danger for delete
        self.btn_clear.clicked.connect(self.clear_cache)

        btn_layout = QVBoxLayout()
        btn_layout.addWidget(self.btn_run)
        btn_layout.addWidget(self.btn_clear)
        input_layout.addLayout(btn_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        input_layout.addWidget(self.progress_bar)

        input_layout.addStretch()
        splitter.addWidget(input_widget)

        # Right Side: Outputs
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)

        self.tabs_output = QTabWidget()
        self.tab_story = QPlainTextEdit()
        self.tab_story.setReadOnly(True)

        self.tab_portraits = QWidget()
        self.portrait_layout = QGridLayout(self.tab_portraits)
        # Wrap in ScrollArea
        scroll_portraits = QScrollArea()
        scroll_portraits.setWidgetResizable(True)
        scroll_portraits.setWidget(self.tab_portraits)

        self.tab_video = QLabel("Video final sẽ hiển thị ở đây (đường dẫn)")
        self.tab_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tab_video.setWordWrap(True)

        self.tabs_output.addTab(self.tab_story, "Cốt truyện (Story)")
        self.tabs_output.addTab(scroll_portraits, "Nhân vật (Portraits)")
        self.tabs_output.addTab(self.tab_video, "Video")

        output_layout.addWidget(self.tabs_output)
        splitter.addWidget(output_widget)

        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 6)

    def clear_cache(self):
        """Delete all files in the working directory to force a fresh run."""
        import shutil

        # Default working dir from config is usually .working_dir/idea2video
        target_dir = ".working_dir/idea2video"

        if os.path.exists(target_dir):
            reply = QMessageBox.question(
                self,
                "Xác nhận",
                f"Bạn có chắc muốn xóa toàn bộ dữ liệu cũ trong {target_dir}?\nThao tác này không thể hoàn tác.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                try:
                    shutil.rmtree(target_dir)
                    os.makedirs(target_dir, exist_ok=True)
                    QMessageBox.information(self, "Đã xóa", "Cache đã được xóa sạch. Bạn có thể chạy ý tưởng mới ngay.")

                    self.tab_story.clear()
                    while self.portrait_layout.count():
                        child = self.portrait_layout.takeAt(0)
                        if child.widget():
                            child.widget().deleteLater()
                    self.tab_video.setText("Video final sẽ hiển thị ở đây (đường dẫn)")

                except Exception as e:
                    QMessageBox.critical(self, "Lỗi", f"Không thể xóa cache: {e}")
        else:
            QMessageBox.information(self, "Thông báo", "Cache đã trống.")

    def set_progress_label(self, text):
        self.progress_bar.setFormat(f"{text} %p%")

    @asyncSlot()
    async def run_pipeline(self):
        idea = self.txt_idea.toPlainText()
        requirement = self.txt_requirement.toPlainText()
        style = self.txt_style.text()

        if not idea:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập ý tưởng!")
            return

        self.btn_run.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate

        try:
            # Init Pipeline
            logging.info("Initializing Pipeline from configs/idea2video.yaml...")
            self.set_progress_label("Initializing...")
            pipeline = Idea2VideoPipeline.init_from_config(config_path="configs/idea2video.yaml")
            self.pipeline = pipeline
            self.working_dir = pipeline.working_dir

            # Step 1: Develop Story
            self.set_progress_label("Developing Story...")
            story = await pipeline.develop_story(idea=idea, user_requirement=requirement)
            self.tab_story.setPlainText(story)
            self.tabs_output.setCurrentIndex(0)

            # Step 2: Extract Characters
            self.set_progress_label("Extracting Characters...")
            characters = await pipeline.extract_characters(story=story)

            # Step 3: Portraits
            self.set_progress_label("Generating Portraits...")
            registry = await pipeline.generate_character_portraits(characters, None, style)
            self.display_portraits(registry)
            self.tabs_output.setCurrentIndex(1)

            # Step 4: Write Script
            self.set_progress_label("Writing Script...")
            scene_scripts = await pipeline.write_script_based_on_story(story=story, user_requirement=requirement)

            # Step 5: Generate Scenes
            from pipelines.script2video_pipeline import Script2VideoPipeline

            all_video_paths = []
            total_scenes = len(scene_scripts)

            for idx, scene_script in enumerate(scene_scripts):
                self.progress_bar.setRange(0, total_scenes)
                self.progress_bar.setValue(idx)
                self.set_progress_label(f"Generating Scene {idx+1}/{total_scenes}")

                scene_working_dir = os.path.join(pipeline.working_dir, f"scene_{idx}")
                os.makedirs(scene_working_dir, exist_ok=True)

                s2v_pipeline = Script2VideoPipeline(
                    chat_model=pipeline.chat_model,
                    image_generator=pipeline.image_generator,
                    video_generator=pipeline.video_generator,
                    working_dir=scene_working_dir,
                )

                final_path = await s2v_pipeline(
                    script=scene_script,
                    user_requirement=requirement,
                    style=style,
                    characters=characters,
                    character_portraits_registry=registry,
                )
                all_video_paths.append(final_path)

            self.progress_bar.setValue(total_scenes)

            # Step 6: Concatenate
            self.set_progress_label("Concatenating Final Video...")
            self.progress_bar.setRange(0, 0)

            final_video_path = os.path.join(pipeline.working_dir, "final_video.mp4")

            def concat_videos():
                # Use pipelines logic manually since we are outside valid context mostly
                clips = [VideoFileClip(p) for p in all_video_paths]
                final = concatenate_videoclips(clips)
                final.write_videofile(final_video_path)
                for c in clips:
                    c.close()

            await asyncio.to_thread(concat_videos)

            self.tabs_output.setCurrentIndex(2)
            self.tab_video.setText(f"Video Saved at:\n{final_video_path}")
            QMessageBox.information(self, "Hoàn tất", f"Video đã tạo xong!\n{final_video_path}")

        except Exception as e:
            logging.error(f"Error running pipeline: {e}")
            QMessageBox.critical(self, "Lỗi", f"Có lỗi xảy ra: {str(e)}")

        finally:
            self.btn_run.setEnabled(True)
            self.progress_bar.setVisible(False)

    def display_portraits(self, registry):
        # Clear layout
        while self.portrait_layout.count():
            child = self.portrait_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        row, col = 0, 0
        for char_name, data in registry.items():
            if 'front' in data:
                path = data['front']['path']
                abs_path = os.path.abspath(path)

                if not os.path.exists(abs_path):
                    logging.warning(f"Portrait not found at: {abs_path}")
                    continue

                lbl_img = QLabel()
                pixmap = QPixmap(abs_path)

                if pixmap.isNull():
                    logging.warning(f"Failed to load image at: {abs_path}")
                    lbl_img.setText(f"Error loading\n{char_name}")
                else:
                    lbl_img.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

                lbl_name = QLabel(char_name)
                lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

                container = QWidget()
                vbox = QVBoxLayout(container)
                vbox.addWidget(lbl_img)
                vbox.addWidget(lbl_name)

                self.portrait_layout.addWidget(container, row, col)
                col += 1
                if col > 2:
                    col = 0
                    row += 1
