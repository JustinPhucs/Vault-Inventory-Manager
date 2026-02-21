import sys
import os
import json
import ctypes
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QListWidget, QTableView, QLabel, QHeaderView,
    QFrame, QAbstractItemView, QPushButton, QStackedWidget,
    QStatusBar, QFileDialog, QListWidgetItem, QStyle
)
from PyQt6.QtCore import (
    Qt, pyqtSignal, QObject, QAbstractTableModel, QSortFilterProxyModel,
    QTimer, QModelIndex, QSize
)
from PyQt6.QtGui import QColor, QFont, QKeySequence, QAction, QIcon, QPixmap, QPainter

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- THIẾT LẬP WINDOWS API CHO DARK MODE TITLE BAR ---
def apply_immersive_dark_mode(window):
    if sys.platform == "win32":
        try:
            hwnd = int(window.winId())
            dwmapi = ctypes.WinDLL("dwmapi")
            # DWMWA_USE_IMMERSIVE_DARK_MODE = 20, older builds use 19
            value = ctypes.c_int(1)
            dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(value), ctypes.sizeof(value))
            dwmapi.DwmSetWindowAttribute(hwnd, 19, ctypes.byref(value), ctypes.sizeof(value)) # Fallback cho Win 10 cũ
        except Exception as e:
            print(f"Lỗi ép Dark Mode Title Bar: {e}")

# --- BIẾN TOÀN CỤC: STYLESHEET (MODERN CLEAN) ---
MODERN_CLEAN_STYLESHEET = """
QMainWindow {
    background-color: #1A1A1A;
}

/* ScrollBars Customization */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #404040;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #4E4E4E;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    height: 0px;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}

QScrollBar:horizontal {
    border: none;
    background: transparent;
    height: 8px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:horizontal {
    background: #404040;
    min-width: 20px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal:hover {
    background: #4E4E4E;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
    width: 0px;
}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: transparent;
}

/* UI Elements */
#TopBar {
    background-color: #1A1A1A;
    border-bottom: 1px solid #2A2A2A;
}
#Sidebar {
    background-color: #1E1E1E;
    border-radius: 10px;
    border: 1px solid #2A2A2A;
}
#RightArea {
    background-color: #1E1E1E;
    border-radius: 10px;
    border: 1px solid #2A2A2A;
}
#ErrorBanner {
    background-color: rgba(220, 38, 38, 0.1);
    color: #F87171;
    border: 1px solid rgba(220, 38, 38, 0.2);
    border-radius: 8px;
    padding: 8px;
    font-weight: 500;
}
#SidebarHeader {
    color: #888888;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
}
#StatusIndicatorLive {
    color: #2ECC71;
    font-weight: 600;
    font-size: 12px;
}
#StatusIndicatorOffline {
    color: #737373;
    font-weight: 600;
    font-size: 12px;
}

/* Buttons */
QPushButton {
    background-color: #262626;
    border: 1px solid #333333;
    border-radius: 8px;
    color: #E5E5E5;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #333333;
    border: 1px solid #404040;
}
QPushButton:pressed {
    background-color: #1A1A1A;
}
QPushButton#BtnIcon {
    background: transparent;
    border: none;
    color: #888888;
    padding: 6px;
    border-radius: 8px;
}
QPushButton#BtnIcon:hover {
    background-color: #262626;
    color: #E5E5E5;
}

/* Input */
QLineEdit {
    background-color: #1A1A1A;
    border: 1px solid #2A2A2A;
    border-radius: 8px;
    color: #E5E5E5;
    padding: 10px 16px;
    font-size: 13px;
    selection-background-color: #4F7DF3;
    selection-color: #FFFFFF;
}
QLineEdit:focus {
    border: 1px solid #4F7DF3;
    background-color: #1E1E1E;
}

/* List & Tables */
QListWidget {
    background-color: transparent;
    border: none;
    color: #A3A3A3;
    font-size: 13px;
    outline: none;
}
QListWidget::item {
    padding: 8px 14px;
    margin: 2px 8px;
    border-radius: 8px;
}
QListWidget::item:hover {
    background-color: #262626;
    color: #E5E5E5;
}
QListWidget::item:selected {
    background-color: rgba(79, 125, 243, 0.1);
    color: #4F7DF3;
    font-weight: 600;
    border-left: 3px solid #4F7DF3;
}

QTableView {
    background-color: transparent;
    border: none;
    color: #D4D4D4;
    font-size: 13px;
    outline: none;
    gridline-color: transparent;
}
QTableView::item {
    padding: 6px 12px;
    border-bottom: 1px solid #222222;
}
QTableView::item:hover {
    background-color: #222222;
}
QTableView::item:selected {
    background-color: rgba(79, 125, 243, 0.15);
    color: #FFFFFF;
}

QHeaderView::section {
    background-color: transparent;
    color: #888888;
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid #2A2A2A;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
}
QHeaderView::section:hover {
    color: #E5E5E5;
    background-color: #262626;
}

/* Status Bar */
QStatusBar {
    background-color: #1A1A1A;
    color: #888888;
    border-top: 1px solid #2A2A2A;
    font-size: 12px;
}
QStatusBar::item {
    border: none;
}
#PathLabel {
    color: #4F7DF3;
    font-weight: 600;
}
#PathLabel:hover {
    color: #6B94FF;
    text-decoration: underline;
}

/* Empty State */
#EmptyText {
    color: #888888;
    font-size: 14px;
    margin-top: 12px;
}
"""

def create_color_icon(color_hex):
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setBrush(QColor(color_hex))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(0, 0, 16, 16, 4, 4)
    painter.end()
    return QIcon(pixmap)

# --- MODEL / VIEW ARCHITECTURE ---
class VaultTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data or []
        self._headers = ["Kho chứa", "Vị trí", "Số lượng", "Tên vật phẩm"]

    def update_data(self, new_data):
        self.beginResetModel()
        self._data = new_data
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        
        row = index.row()
        col = index.column()
        item = self._data[row]

        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0: return item.get('vault', '')
            if col == 1: return f"Slot {item.get('slot', '')}"
            if col == 2: return int(item.get('count', 0))
            if col == 3: return item.get('name', '')
            
        elif role == Qt.ItemDataRole.ForegroundRole:
            if col == 0:
                return QColor("#888888")
            if col == 2: # Quantity
                return QColor("#888888")
            if col == 3: # Name
                return QColor("#E5E5E5") # Light text for name, no neon blue
            return QColor("#D4D4D4")

        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if col == 1 or col == 2:
                return Qt.AlignmentFlag.AlignCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._headers[section]
        return None

class VaultSortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self._filter_vault = ""
        self._filter_text = ""

    def setFilterVault(self, vault):
        self._filter_vault = vault
        self.invalidateFilter()

    def setFilterText(self, text):
        self._filter_text = text.lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        item = model._data[source_row]
        
        # 1. Filter by vault
        if self._filter_vault and self._filter_vault != "TẤT CẢ CÁC KHO":
            if item.get('vault') != self._filter_vault:
                return False
                
        # 2. Filter by search text
        if self._filter_text:
            name = str(item.get('name', '')).lower()
            item_id = str(item.get('id', '')).lower()
            if self._filter_text not in name and self._filter_text not in item_id:
                return False
                
        return True

# --- WATCHDOG: DEBOUNCED THEO DÕI FILE ---
class LogWatcherHandler(FileSystemEventHandler, QObject):
    file_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._emit_signal)
        self.debounce_ms = 200

    def on_modified(self, event):
        if event.src_path.endswith(".json"):
            self.timer.start(self.debounce_ms)

    def on_created(self, event):
        if event.src_path.endswith(".json"):
            self.timer.start(self.debounce_ms)
            
    def _emit_signal(self):
        self.file_changed.emit()

# --- GIAO DIỆN CHÍNH ---
class VaultManagerApp(QMainWindow):
    def __init__(self):
        super().__init__() # Phải gọi ông này đầu tiên để khởi tạo cửa sổ nhé! 🚀
        
        # 1. Xử lý đường dẫn Icon động (để chạy được trên mọi máy)
        # Nếu đóng gói bằng PyInstaller, nó sẽ tìm icon trong thư mục đi kèm
        script_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(script_dir, "icon", "icon.ico")
        
        # Nếu file icon tồn tại thì mới set, tránh lỗi crash
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            # Fallback cho đường dẫn tuyệt đối của Mai Cồ khi đang code
            self.setWindowIcon(QIcon(r"C:\Users\Administrator\Desktop\FULL PROJECT MINECRAFT\vault-item-logger-1.21.4\Vault Inventory Manager\icon\icon.ico"))

        self.setWindowTitle("VAULT INVENTORY")
        self.resize(1150, 750)
        self.log_path = ""
        
        # UI Icons (Các icon hệ thống có sẵn)
        self.icon_folder = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        self.icon_refresh = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        self.icon_all = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
        self.icon_error = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
        
        self.vault_icon = create_color_icon("#4F7DF3")
        
        # Model
        self.source_model = VaultTableModel()
        self.proxy_model = VaultSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.source_model)
        self.proxy_model.setSortRole(Qt.ItemDataRole.DisplayRole)
        self.proxy_model.setDynamicSortFilter(True)
        
        self.observer = None
        
        self.setup_ui()
        self.setStyleSheet(MODERN_CLEAN_STYLESHEET)
        apply_immersive_dark_mode(self)
        
        self.setup_shortcuts()
        
        # Default dir check via config
        if getattr(sys, 'frozen', False):
            config_dir = os.path.dirname(sys.executable)
        else:
            config_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(config_dir, "config.json")
        config_data = self.load_config()
        default_path = config_data.get("default_path", "")
        
        if default_path and os.path.exists(default_path):
            self.start_watching(default_path)
        else:
            self.show_empty_path_state()

    def setup_ui(self):
        root_widget = QWidget()
        self.setCentralWidget(root_widget)
        root_layout = QVBoxLayout(root_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # --- TOP TOOLBAR ---
        top_bar = QFrame()
        top_bar.setObjectName("TopBar")
        top_bar.setFixedHeight(50)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(15, 0, 15, 0)
        
        self.btn_toggle_sidebar = QPushButton("≡")
        self.btn_toggle_sidebar.setObjectName("BtnIcon")
        self.btn_toggle_sidebar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_sidebar.clicked.connect(self.toggle_sidebar)
        self.btn_toggle_sidebar.setToolTip("Toggle Sidebar")
        
        # App Title instead of path
        lbl_app_title = QLabel("VAULT INVENTORY")
        lbl_app_title.setFont(QFont("Segoe UI", 25, QFont.Weight.Bold))
        lbl_app_title.setStyleSheet("color: #E5E5E5; letter-spacing: 0.5px;")
        
        self.lbl_status_indicator = QLabel("● OFFLINE")
        self.lbl_status_indicator.setObjectName("StatusIndicatorOffline")
        
        top_layout.addWidget(self.btn_toggle_sidebar)
        top_layout.addSpacing(10)
        top_layout.addWidget(lbl_app_title)
        top_layout.addStretch()
        top_layout.addWidget(self.lbl_status_indicator)

        # --- MAIN CONTENT ---
        main_content = QWidget()
        main_layout = QHBoxLayout(main_content)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 1. Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 15, 0, 10)
        
        sidebar_label = QLabel("DANH SÁCH VAULT")
        sidebar_label.setObjectName("SidebarHeader")
        sidebar_label.setContentsMargins(15, 0, 15, 5)
        
        self.vault_list = QListWidget()
        self.vault_list.itemClicked.connect(self.on_vault_selected)
        
        sidebar_layout.addWidget(sidebar_label)
        sidebar_layout.addWidget(self.vault_list)

        # 2. Right Area
        right_area = QFrame()
        right_area.setObjectName("RightArea")
        right_layout = QVBoxLayout(right_area)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(10)

        # Error Banner (Hidden by default)
        self.error_banner = QLabel("")
        self.error_banner.setObjectName("ErrorBanner")
        self.error_banner.setVisible(False)
        self.error_banner.setWordWrap(True)

        # Thanh tìm kiếm & Utils
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm theo tên hoặc ID (ví dụ: diamond)...")
        self.search_input.textChanged.connect(self.on_search_changed)
        
        self.btn_clear_search = QPushButton("✕")
        self.btn_clear_search.setObjectName("BtnIcon")
        self.btn_clear_search.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_search.clicked.connect(lambda: self.search_input.clear())
        self.btn_clear_search.hide()
        self.search_input.textChanged.connect(lambda t: self.btn_clear_search.setVisible(bool(t)))
        
        # Refresh Button
        self.btn_refresh = QPushButton()
        self.btn_refresh.setIcon(self.icon_refresh)
        self.btn_refresh.setToolTip("Làm mới dữ liệu thủ công")
        self.btn_refresh.clicked.connect(self.reload_data)
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.setFixedSize(38, 38)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btn_clear_search)
        search_layout.addWidget(self.btn_refresh)
        
        # Stacked Widget
        self.stack = QStackedWidget()
        
        # Bảng hiển thị tối ưu
        self.table = QTableView()
        self.table.setModel(self.proxy_model)
        self.table.setSortingEnabled(True)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        
        self.table.setColumnWidth(0, 160)
        self.table.setColumnWidth(1, 90)
        self.table.setColumnWidth(2, 100)
        
        self.table.selectionModel().selectionChanged.connect(self.update_selection_metrics)
        self.table.doubleClicked.connect(self.copy_single_row)

        # Empty State
        self.empty_state = QWidget()
        empty_layout = QVBoxLayout(self.empty_state)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_empty_icon = QLabel("📦")
        lbl_empty_icon.setFont(QFont("Segoe UI Emoji", 48))
        lbl_empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_empty_text = QLabel("Không tìm thấy vật phẩm.")
        self.lbl_empty_text.setObjectName("EmptyText")
        self.lbl_empty_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(lbl_empty_icon)
        empty_layout.addWidget(self.lbl_empty_text)

        self.stack.addWidget(self.table)
        self.stack.addWidget(self.empty_state)

        right_layout.addWidget(self.error_banner)
        right_layout.addLayout(search_layout)
        right_layout.addWidget(self.stack)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(right_area)

        # --- STATUS BAR ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.lbl_path = QLabel("Chọn thư mục Vault Logs...")
        self.lbl_path.setObjectName("PathLabel")
        self.lbl_path.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_path.mousePressEvent = self.change_directory
        self.lbl_path.setToolTip("Nhấn để thay đổi thư mục theo dõi")
        
        self.lbl_metrics = QLabel(" | Tổng: 0 Items | 0 Vaults ")
        self.lbl_selection = QLabel("")
        self.lbl_last_update = QLabel(" Cập nhật cuối: Chưa từng ")
        
        # Layout components onto status bar
        self.status_bar.addWidget(QLabel(" 📁 "))
        self.status_bar.addWidget(self.lbl_path)
        self.status_bar.addWidget(self.lbl_metrics)
        self.status_bar.addWidget(self.lbl_selection)
        self.status_bar.addPermanentWidget(self.lbl_last_update)

        root_layout.addWidget(top_bar)
        root_layout.addWidget(main_content)

        self.sidebar_visible = True

    def setup_shortcuts(self):
        self.copy_shortcut = QAction("Copy", self)
        self.copy_shortcut.setShortcut(QKeySequence.StandardKey.Copy)
        self.copy_shortcut.triggered.connect(self.copy_selection)
        self.addAction(self.copy_shortcut)
        
        self.search_shortcut = QAction("Focus Search", self)
        self.search_shortcut.setShortcut(QKeySequence.StandardKey.Find)
        self.search_shortcut.triggered.connect(lambda: self.search_input.setFocus())
        self.addAction(self.search_shortcut)
        
        self.refresh_shortcut = QAction("Refresh", self)
        self.refresh_shortcut.setShortcut(QKeySequence(Qt.Key.Key_F5))
        self.refresh_shortcut.triggered.connect(self.reload_data)
        self.addAction(self.refresh_shortcut)

    def set_status_live(self, is_live):
        if is_live:
            self.lbl_status_indicator.setText("● LIVE")
            self.lbl_status_indicator.setObjectName("StatusIndicatorLive")
        else:
            self.lbl_status_indicator.setText("● OFFLINE")
            self.lbl_status_indicator.setObjectName("StatusIndicatorOffline")
        self.lbl_status_indicator.style().unpolish(self.lbl_status_indicator)
        self.lbl_status_indicator.style().polish(self.lbl_status_indicator)

    def toggle_sidebar(self):
        self.sidebar_visible = not self.sidebar_visible
        self.sidebar.setVisible(self.sidebar_visible)

    def change_directory(self, event):
        dir_path = QFileDialog.getExistingDirectory(self, "Chọn Thư mục Vault Logs", self.log_path)
        if dir_path:
            norm_path = os.path.normpath(dir_path)
            self.start_watching(norm_path)
            self.save_config(norm_path)

    def show_empty_path_state(self):
        self.lbl_path.setText("Click để chọn thư mục...")
        self.set_status_live(False)
        self.stack.setCurrentIndex(1)
        self.lbl_empty_text.setText("Chưa chọn thư mục.\nHãy chọn đường dẫn chứa các file .json của vault.")
        self.vault_list.clear()
        self.source_model.update_data([])
        self.update_metrics_bar(0)
        self.error_banner.setVisible(False)

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def save_config(self, path):
        try:
            config_data = self.load_config()
            config_data["default_path"] = path
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            print(f"Lỗi lưu config: {e}")

    def start_watching(self, path):
        if not os.path.exists(path):
            self.show_empty_path_state()
            return
            
        self.log_path = path
        short_path = path if len(path) < 50 else f"...{path[-47:]}"
        self.lbl_path.setText(f"{short_path}")
        self.lbl_path.setToolTip(path)
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        self.handler = LogWatcherHandler()
        self.handler.file_changed.connect(self.reload_data)
        
        self.observer = Observer()
        self.observer.schedule(self.handler, path, recursive=False)
        self.observer.start()
        
        self.set_status_live(True)
        self.reload_data()

    def reload_data(self):
        if not self.log_path or not os.path.exists(self.log_path):
            return

        # Lưu lại trạng thái thanh cuộn để chống flickering
        scroll_pos = self.table.verticalScrollBar().value()
        self.table.setUpdatesEnabled(False)

        current_vaults = [f for f in os.listdir(self.log_path) if f.endswith(".json")]
        
        parsed_data = []
        vault_counts = {}
        error_vaults = []
        
        for file in sorted(current_vaults):
            vault_name = file.replace(".json", "").capitalize()
            vault_counts[vault_name] = 0
            file_path = os.path.join(self.log_path, file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    items = json.load(f)
                    for item in items:
                        item['vault'] = vault_name
                        parsed_data.append(item)
                        vault_counts[vault_name] += 1
            except Exception as e:
                error_vaults.append(f"{vault_name} ({str(e)})")

        # Xử lý banner lỗi
        if error_vaults:
            self.error_banner.setText(f"⚠️ Phát hiện lỗi khi đọc file JSON: {', '.join(error_vaults)}")
            self.error_banner.setVisible(True)
        else:
            self.error_banner.setVisible(False)

        # Cập nhật danh sách vault (thay vì Emoji, dùng QIcon)
        selected_vault = "TẤT CẢ CÁC KHO"
        if self.vault_list.currentItem():
            selected_vault = self.vault_list.currentItem().data(Qt.ItemDataRole.UserRole)
            
        self.vault_list.clear()
        
        item_all = QListWidgetItem(" Tất cả các kho")
        item_all.setIcon(self.icon_all)
        item_all.setData(Qt.ItemDataRole.UserRole, "TẤT CẢ CÁC KHO")
        self.vault_list.addItem(item_all)
        
        for v_name in sorted(vault_counts.keys()):
            if any(v_name in ev for ev in error_vaults):
                item = QListWidgetItem(f" {v_name} (Lỗi)")
                item.setIcon(self.icon_error)
            else:
                item = QListWidgetItem(f" {v_name} ({vault_counts[v_name]})")
                item.setIcon(self.vault_icon)
                
            item.setData(Qt.ItemDataRole.UserRole, v_name)
            self.vault_list.addItem(item)

        # Phục hồi dòng đang chọn
        matched = False
        for i in range(self.vault_list.count()):
            val = self.vault_list.item(i).data(Qt.ItemDataRole.UserRole)
            if val == selected_vault:
                self.vault_list.setCurrentRow(i)
                matched = True
                break
                
        if not matched and self.vault_list.count() > 0:
            self.vault_list.setCurrentRow(0)

        # Nạp dữ liệu
        self.source_model.update_data(parsed_data)
        
        # Dashboard updates
        self.update_metrics_bar(len(vault_counts))
        self.lbl_last_update.setText(f" Cập nhật cuối: {datetime.now().strftime('%H:%M:%S')} ")
        
        self.check_empty_state()

        # Áp dụng lại thanh cuộn và render lại giao diện
        self.table.verticalScrollBar().setValue(scroll_pos)
        self.table.setUpdatesEnabled(True)

    def on_vault_selected(self, item):
        vault_name = item.data(Qt.ItemDataRole.UserRole)
        if vault_name == "TẤT CẢ CÁC KHO":
            self.proxy_model.setFilterVault("")
        else:
            self.proxy_model.setFilterVault(vault_name)
        self.check_empty_state()

    def on_search_changed(self, text):
        self.proxy_model.setFilterText(text)
        self.check_empty_state()

    def check_empty_state(self):
        if self.proxy_model.rowCount() == 0:
            if self.search_input.text():
                self.lbl_empty_text.setText(f"Không tìm kết quả nào cho '{self.search_input.text()}'")
            else:
                self.lbl_empty_text.setText("Kho rỗng. Chưa có vật phẩm nào.")
            self.stack.setCurrentIndex(1)
        else:
            self.stack.setCurrentIndex(0)

    def update_metrics_bar(self, num_vaults):
        total_items = self.source_model.rowCount()
        self.lbl_metrics.setText(f" | Tổng: {total_items} items trong {num_vaults} vaults ")

    def update_selection_metrics(self, selected, deselected):
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            self.lbl_selection.setText("")
            return
            
        total_qty = 0
        for idx in indexes:
            qty_idx = self.proxy_model.index(idx.row(), 2)
            qty = self.proxy_model.data(qty_idx, Qt.ItemDataRole.DisplayRole)
            try:
                total_qty += int(qty)
            except:
                pass
                
        if len(indexes) == 1:
            self.lbl_selection.setText("")
        else:
            self.lbl_selection.setText(f" | Đang chọn {len(indexes)} dòng (Tổng: {total_qty}) ")

    def copy_single_row(self, index):
        if not index.isValid(): return
        row = index.row()
        
        info = []
        for col in range(self.proxy_model.columnCount()):
            header = self.source_model.headerData(col, Qt.Orientation.Horizontal)
            data = self.proxy_model.data(self.proxy_model.index(row, col), Qt.ItemDataRole.DisplayRole)
            info.append(f"{header}: {data}")
            
        copy_text = " | ".join(info)
        QApplication.clipboard().setText(copy_text)
        self.show_copied_status()

    def copy_selection(self):
        indexes = self.table.selectionModel().selectedRows()
        if not indexes: return
            
        indexes = sorted(indexes, key=lambda x: x.row())
        headers = [self.source_model.headerData(i, Qt.Orientation.Horizontal) for i in range(self.source_model.columnCount())]
        copy_text = "\t".join(headers) + "\n"
        
        for idx in indexes:
            row_data = []
            for col in range(self.proxy_model.columnCount()):
                col_idx = self.proxy_model.index(idx.row(), col)
                data = self.proxy_model.data(col_idx, Qt.ItemDataRole.DisplayRole)
                row_data.append(str(data))
            copy_text += "\t".join(row_data) + "\n"
            
        QApplication.clipboard().setText(copy_text)
        self.show_copied_status()
        
    def show_copied_status(self):
        orig_text = self.lbl_selection.text()
        self.lbl_selection.setText(" | ✅ Đã copy vào Clipboard! ")
        QTimer.singleShot(2500, lambda: self.lbl_selection.setText(orig_text))

    def closeEvent(self, event):
        if self.observer:
            self.observer.stop()
            self.observer.join()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = VaultManagerApp()
    window.show()
    sys.exit(app.exec())