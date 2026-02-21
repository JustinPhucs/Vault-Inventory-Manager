import sys
import os
import shutil
import ctypes
import pathspec
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QTextEdit, QLabel, QProgressBar, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QPalette

# --- Windows API để ép Immersive Dark Mode ---
def set_immersive_dark_mode(win_id):
    if sys.platform == "win32":
        try:
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            set_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
            rendering_policy = ctypes.c_int(1)
            set_attribute(win_id, DWMWA_USE_IMMERSIVE_DARK_MODE, 
                          ctypes.byref(rendering_policy), ctypes.sizeof(rendering_policy))
        except Exception as e:
            print(f"Lỗi set Dark Mode Title Bar: {e}")

# --- Worker Thread để không bị đơ giao diện khi copy file nặng ---
class CopyWorker(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal(str)

    def run(self):
        try:
            root_dir = os.getcwd()
            folder_name = os.path.basename(root_dir)
            output_dir = os.path.join(os.path.dirname(root_dir), f"{folder_name}-Output")
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            gitignore_path = os.path.join(root_dir, '.gitignore')
            if not os.path.exists(gitignore_path):
                self.log.emit("❌ Không tìm thấy file .gitignore!")
                return

            with open(gitignore_path, 'r', encoding='utf-8') as f:
                spec = pathspec.PathSpec.from_lines('gitwildmatch', f)

            files_to_copy = []
            for root, dirs, files in os.walk(root_dir):
                # Loại bỏ folder Output và .git để tránh loop vô tận
                if output_dir in root or '.git' in root:
                    continue
                
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, root_dir)
                    
                    if not spec.match_file(rel_path):
                        files_to_copy.append((full_path, rel_path))

            total = len(files_to_copy)
            for i, (src, rel) in enumerate(files_to_copy):
                dest = os.path.join(output_dir, rel)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(src, dest)
                
                prog = int(((i + 1) / total) * 100)
                self.progress.emit(prog)
                self.log.emit(f"🚚 Copied: {rel}")

            self.finished.emit(output_dir)
        except Exception as e:
            self.log.emit(f"💥 Lỗi: {str(e)}")

# --- Giao diện chính Sleek Carbon ---
class SleekPorter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        set_immersive_dark_mode(int(self.winId()))

    def init_ui(self):
        self.setWindowTitle("GitIgnore Porter v1.0")
        self.setFixedSize(600, 450)
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QWidget { color: #E0E0E0; font-family: 'Segoe UI', sans-serif; }
            QFrame#MainCard { 
                background-color: #1E1E1E; 
                border-radius: 15px; 
                border: 1px solid #333333;
            }
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #2563EB; }
            QPushButton:pressed { background-color: #1D4ED8; }
            QTextEdit {
                background-color: #121212;
                border: 1px solid #333333;
                border-radius: 10px;
                color: #A0A0A0;
                font-size: 11px;
            }
            QProgressBar {
                border: 1px solid #333333;
                border-radius: 5px;
                text-align: center;
                background-color: #121212;
            }
            QProgressBar::chunk {
                background-color: #3B82F6;
                border-radius: 4px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)

        self.card = QFrame()
        self.card.setObjectName("MainCard")
        card_layout = QVBoxLayout(self.card)
        
        self.label_title = QLabel("📦 PROJECT CLEAN EXPORTER")
        self.label_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #3B82F6; margin-bottom: 5px;")
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_desc = QLabel(f"Root: {os.path.basename(os.getcwd())}")
        self.label_desc.setStyleSheet("color: #888888; margin-bottom: 10px;")
        self.label_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        
        self.pbar = QProgressBar()
        self.pbar.setValue(0)

        self.btn_start = QPushButton("🚀 Bắt đầu trích xuất (Clean Copy)")
        self.btn_start.clicked.connect(self.start_process)

        card_layout.addWidget(self.label_title)
        card_layout.addWidget(self.label_desc)
        card_layout.addWidget(self.log_area)
        card_layout.addWidget(self.pbar)
        card_layout.addWidget(self.btn_start)

        layout.addWidget(self.card)

    def start_process(self):
        self.btn_start.setEnabled(False)
        self.log_area.clear()
        self.log_area.append("🔍 Đang phân tích file .gitignore...")
        
        self.worker = CopyWorker()
        self.worker.log.connect(lambda msg: self.log_area.append(msg))
        self.worker.progress.connect(lambda val: self.pbar.setValue(val))
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, out_path):
        self.log_area.append(f"\n✅ HOÀN TẤT!")
        self.log_area.append(f"📂 Đã lưu tại: {out_path}")
        self.btn_start.setEnabled(True)
        os.startfile(out_path) # Tự động mở folder khi xong

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SleekPorter()
    window.show()
    sys.exit(app.exec())