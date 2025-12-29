from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QTextEdit, QLabel, QComboBox, QFrame, QDialog, QListWidget
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt, QSize
from rsa_widget import RSAPanel
from railfence import encrypt_railfence, decrypt_railfence



class CryptoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crypto GUI Project")
        self.setGeometry(200, 100, 1100, 600)

        self.is_dark = True   # الوضع الافتراضي Dark

        # ----------------- Layout رئيسي -----------------
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        # ----------------- Taskbar -----------------
        self.taskbar_widget = QFrame()
        self.taskbar_widget.setFixedWidth(250)
        self.taskbar_layout = QVBoxLayout(self.taskbar_widget)
        self.taskbar_layout.setSpacing(25)
        self.taskbar_layout.setContentsMargins(10, 20, 10, 20)

        # ----------------- Buttons Algorithms -----------------
        self.buttons = {}
        algos = ["Multiplicative", "OTP", "Rail Fence", "RSA", "DES", "AES ShiftRows"]
        for name in algos:
            btn = QPushButton(name)
            btn.setFixedHeight(60)
            btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
            self.taskbar_layout.addWidget(btn)
            self.buttons[name] = btn

        self.taskbar_layout.addStretch()

        # ----------------- Home + Dark + Light + Info -----------------
        icon_bar = QHBoxLayout()

        def safe_icon(theme_name, fallback_text):
            icon = QIcon.fromTheme(theme_name)
            if icon.isNull():
                return fallback_text
            return icon

        # زر Home
        self.home_btn = QPushButton()
        home_icon = safe_icon("go-home", "🏠")
        if isinstance(home_icon, QIcon):
            self.home_btn.setIcon(home_icon)
            self.home_btn.setIconSize(QSize(22, 22))
        else:
            self.home_btn.setText(home_icon)
        self.home_btn.setFixedSize(40, 40)
        self.home_btn.clicked.connect(self.show_home)
        self.home_btn.setStyleSheet("""
            QPushButton {
                background-color: #3949AB;
                border-radius: 20px;
                font-size: 18px;
                color: white;
            }
            QPushButton:hover {
                background-color: #5C6BC0;
            }
        """)

        # زر Dark
        self.dark_btn = QPushButton()
        dark_icon = safe_icon("weather-clear-night", "🌙")
        if isinstance(dark_icon, QIcon):
            self.dark_btn.setIcon(dark_icon)
            self.dark_btn.setIconSize(QSize(20, 20))
        else:
            self.dark_btn.setText(dark_icon)
        self.dark_btn.setFixedSize(40, 40)
        self.dark_btn.clicked.connect(self.set_dark)
        self.dark_btn.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                border-radius: 20px;
                font-size: 18px;
                color: white;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)

        # زر Light
        self.light_btn = QPushButton()
        light_icon = safe_icon("weather-sunny", "☀")
        if isinstance(light_icon, QIcon):
            self.light_btn.setIcon(light_icon)
            self.light_btn.setIconSize(QSize(20, 20))
        else:
            self.light_btn.setText(light_icon)
        self.light_btn.setFixedSize(40, 40)
        self.light_btn.clicked.connect(self.set_light)
        self.light_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFD600;
                border-radius: 20px;
                font-size: 18px;
                color: black;
            }
            QPushButton:hover {
                background-color: #FFEA00;
            }
        """)

        # زر Info
        self.info_btn = QPushButton()
        info_icon = safe_icon("help-about", "ℹ")
        if isinstance(info_icon, QIcon):
            self.info_btn.setIcon(info_icon)
            self.info_btn.setIconSize(QSize(20, 20))
        else:
            self.info_btn.setText(info_icon)
        self.info_btn.setFixedSize(40, 40)
        self.info_btn.clicked.connect(self.show_team_info)
        self.info_btn.setStyleSheet("""
            QPushButton {
                background-color: #009688;
                border-radius: 20px;
                font-size: 18px;
                color: white;
            }
            QPushButton:hover {
                background-color: #26A69A;
            }
        """)

        icon_bar.addWidget(self.home_btn)
        icon_bar.addWidget(self.dark_btn)
        icon_bar.addWidget(self.light_btn)
        icon_bar.addWidget(self.info_btn)

        self.taskbar_layout.addLayout(icon_bar)
        self.main_layout.addWidget(self.taskbar_widget)

        # ----------------- Divider -----------------
        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(divider)

        # ----------------- Content Area -----------------
        self.content_frame = QFrame()
        self.content_layout = QVBoxLayout(self.content_frame)
        self.main_layout.addWidget(self.content_frame)

        # ----------------- ربط الأزرار -----------------
        for name, btn in self.buttons.items():
            btn.clicked.connect(lambda checked, n=name: self.show_layout(n))

        # ----------------- تفعيل الثيم الافتراضي -----------------
        self.apply_theme()
        self.show_home()

    # ----------------- Dark Mode -----------------
    def set_dark(self):
        self.is_dark = True
        self.apply_theme()

    # ----------------- Light Mode -----------------
    def set_light(self):
        self.is_dark = False
        self.apply_theme()

    # ----------------- تطبيق الثيم -----------------
    def apply_theme(self):
        if self.is_dark:
            self.setStyleSheet("""
                QWidget { background-color: #1E1E2F; color: #E0E0E0; font-family: 'Segoe UI'; }
                QPushButton { background-color: #5C6BC0; color: white; border-radius: 8px; padding: 6px; }
                QPushButton:hover { background-color: #7986CB; }
                QTextEdit { background-color: #2A2A3D; color: white; border-radius: 10px; padding: 5px; }
                QLabel { color: #81D4FA; font-weight: bold; }
                QComboBox { background-color: #2A2A3D; color: white; border-radius: 8px; }
            """)
        else:
            self.setStyleSheet("""
                QWidget { background-color: #F5F5F5; color: black; font-family: 'Segoe UI'; }
                QPushButton { background-color: #2196F3; color: white; border-radius: 8px; padding: 6px; }
                QPushButton:hover { background-color: #42A5F5; }
                QTextEdit { background-color: white; color: black; border-radius: 10px; padding: 5px; border: 1px solid #BDBDBD; }
                QLabel { color: #0D47A1; font-weight: bold; }
                QComboBox { background-color: white; color: black; border-radius: 8px; }
            """)

    # ----------------- مسح الصفحة -----------------
    def clear_layout(self, layout=None):
        if layout is None:
            layout = self.content_layout
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # ----------------- Home -----------------
    def show_home(self):
        self.clear_layout()
        label = QLabel("Welcome to Cryptography!\n\nTeam 11")
        label.setFont(QFont("Segoe UI", 40, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(label)

    # ----------------- Algorithm Layout -----------------
    def show_layout(self, algo):
        self.clear_layout()

        if algo == "RSA":
            rsa_panel = RSAPanel()
            self.content_layout.addWidget(rsa_panel)
            return
        header = QLabel(algo)
        header.setFont(QFont("Segoe UI", 30, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(header)

        mode = QComboBox()
        mode.addItems(["Encrypt", "Decrypt"])

        input_text = QTextEdit()
        input_text.setPlaceholderText("Enter text...")

        key_text = QTextEdit()
        key_text.setPlaceholderText("Enter key (number)...")

        btn = QPushButton("Run")

        output = QTextEdit()
        output.setReadOnly(True)

        self.content_layout.addWidget(mode)
        self.content_layout.addWidget(input_text)
        self.content_layout.addWidget(key_text)
        self.content_layout.addWidget(btn)
        self.content_layout.addWidget(output)

        
    def show_team_info(self):
        self.clear_layout()  # مسح المحتوى الحالي

        header = QLabel("Team 11 Members")
        header.setFont(QFont("Segoe UI", 30, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(header)

        # Frame داخلي ليظهر أعضاء الفريق
        team_frame = QFrame()
        team_frame.setStyleSheet("""
            QFrame { 
                background-color: #2A2A3D; 
                border-radius: 10px; 
                padding: 10px; 
            }
            QLabel { color: #81D4FA; font-size: 16px; }
        """)
        team_layout = QVBoxLayout(team_frame)

        members = [
            "Sayed Sherif Sayed",
            "Tarek Omar El Sayed",
            "Abdulrahman Samir Mohammed",
            "Mahmoud Abdulrazik Ahmed",
            "Ahmed Abdulnasser",
            "Eman Ashraf Mohammed",
            "Malak Magdy Mohammed",
            "Omnia Khalid Ibrahim",
            "Ahmed Mohammed Mohammed",
            "Saif Khalid Amin",
            "Mohammed Nasr Mohammed"
        ]

        for member in members:
            lbl = QLabel(f"• {member}")
            team_layout.addWidget(lbl)

        self.content_layout.addWidget(team_frame)
        print("Constructor Running!")




# ----------------- Run App -----------------
app = QApplication([])
window = CryptoApp()
window.show()
app.exec()
