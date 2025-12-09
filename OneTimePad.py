import sys
import random
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QFileDialog, QMessageBox, QDialog, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QTimer

# ----------------- Logic Class -----------------
class OTPLogic:
    # ----------------- الأبجدية -----------------
    ENGLISH_ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    
    # تم التعديل هنا: إضافة الأرقام الإنجليزية (0-9) للأبجدية العربية
    # لضمان عمل المفاتيح التي تحتوي على أرقام إنجليزية مع النصوص العربية
    ARABIC_ALPHABET = "ابتثجحخدذرزسشصضطظعغفقكلمنهويا٠١٢٣٤٥٦٧٨٩0123456789"
    
    MIXED_ALPHABET = ENGLISH_ALPHABET + ARABIC_ALPHABET

    # ----------------- توحيد النصوص -----------------
    @staticmethod
    def _normalize_text(text, lang):
        if lang == 'ARABIC':
            text = text.replace('أ', 'ا')
            text = text.replace('إ', 'ا')
            text = text.replace('آ', 'ا')
            text = text.replace('ى', 'ي')
            text = text.replace('ة', 'ه')
            text = text.replace('ؤ', 'و')
            text = text.replace('ئ', 'ي')
        return text

    # ----------------- كشف اللغة -----------------
    @staticmethod
    def detect_language(text):
        arabic_count = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        english_count = sum(1 for c in text if c.isalpha() and 'a' <= c.lower() <= 'z')
        
        if arabic_count > english_count * 0.5:
            return 'ARABIC'
        elif english_count > arabic_count * 0.5:
            return 'ENGLISH'
        else:
            return 'MIXED'

    # ----------------- اختيار الأبجدية -----------------
    @staticmethod
    def _get_alphabet(text):
        lang = OTPLogic.detect_language(text)
        if lang == 'ARABIC':
            return OTPLogic.ARABIC_ALPHABET, lang
        elif lang == 'ENGLISH':
            return OTPLogic.ENGLISH_ALPHABET, lang
        else:
            return OTPLogic.MIXED_ALPHABET, lang

    # ----------------- توليد مفتاح عشوائي -----------------
    @staticmethod
    def generate_key(length, text):
        alphabet, lang = OTPLogic._get_alphabet(text)
        return "".join(random.choice(alphabet) for _ in range(length))

    # ----------------- التشفير -----------------
    @staticmethod
    def encrypt(text, key):
        if len(key) < len(text):
            return None, "Error: Key length must be >= Text length", None
        
        alphabet, lang = OTPLogic._get_alphabet(text)
        n = len(alphabet)
        cipher_text = ""
        steps = []

        normalized_text = OTPLogic._normalize_text(text, lang)
        normalized_key = OTPLogic._normalize_text(key, lang)

        for t_norm, k_norm, t_orig, k_orig in zip(normalized_text, normalized_key, text, key):
            if t_norm in alphabet and k_norm in alphabet:
                t_idx = alphabet.index(t_norm)
                k_idx = alphabet.index(k_norm)
                c_idx = (t_idx + k_idx) % n
                c_char = alphabet[c_idx]
                cipher_text += c_char
                steps.append((t_orig, k_orig, c_char, f"({t_idx}+{k_idx})%{n}={c_idx}"))
            else:
                cipher_text += t_orig
                steps.append((t_orig, k_orig, t_orig, "Ignored"))

        return cipher_text, steps, lang

    # ----------------- فك التشفير -----------------
    @staticmethod
    def decrypt(cipher, key):
        if len(key) < len(cipher):
            return None, "Error: Key length must be >= Cipher length", None
        
        alphabet, lang = OTPLogic._get_alphabet(cipher)
        n = len(alphabet)
        plain_text = ""
        steps = []

        normalized_cipher = OTPLogic._normalize_text(cipher, lang)
        normalized_key = OTPLogic._normalize_text(key, lang)

        for c_norm, k_norm, c_orig, k_orig in zip(normalized_cipher, normalized_key, cipher, key):
            if c_norm in alphabet and k_norm in alphabet:
                c_idx = alphabet.index(c_norm)
                k_idx = alphabet.index(k_norm)
                p_idx = (c_idx - k_idx) % n
                p_char = alphabet[p_idx]
                plain_text += p_char
                steps.append((c_orig, k_orig, p_char, f"({c_idx}-{k_idx})%{n}={p_idx}"))
            else:
                plain_text += c_orig
                steps.append((c_orig, k_orig, c_orig, "Ignored"))

        return plain_text, steps, lang


# ----------------- Visualization Window -----------------
class OTPVisualizer(QDialog):
    def __init__(self, steps, mode="Encrypt", is_dark=True, lang="MIXED"):
        super().__init__()
        self.setWindowTitle(f"OTP Visualization - {mode} ({lang})")
        self.resize(950, 600)
        self.steps = steps
        self.current_step = 0
        self.is_dark = is_dark
        self.lang = lang
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        lbl = QLabel(f"Visualizing {mode} Process")
        lbl.setFont(QFont("Segoe UI", 18, QFont.Bold))
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)

        hint = QLabel(f"Detected Language: {lang}. Logic: Index(Text) +/- Index(Key) % Alphabet_Size")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(hint)
        
        self.table = QTableWidget()
        if mode == "Encrypt":
            headers = ["Input Char", "Key Char", "Math (Index)", "Result"]
        else:
            headers = ["Cipher Char", "Key Char", "Math (Index)", "Result"]
            
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(headers)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        self.status_lbl = QLabel("Starting Animation...")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setFont(QFont("Segoe UI", 12))
        layout.addWidget(self.status_lbl)
        
        self.apply_theme()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.add_next_step)
        self.timer.start(300)

    def add_next_step(self):
        if self.current_step < len(self.steps):
            inp, key, out, eq = self.steps[self.current_step]
            
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(f" '{inp}' "))
            self.table.setItem(row, 1, QTableWidgetItem(f" '{key}' "))
            self.table.setItem(row, 2, QTableWidgetItem(str(eq)))
            self.table.setItem(row, 3, QTableWidgetItem(f" '{out}' "))
            
            self.table.scrollToBottom()
            self.status_lbl.setText(f"Processing char {self.current_step + 1} / {len(self.steps)}")
            self.current_step += 1
        else:
            self.timer.stop()
            self.status_lbl.setText("Visualization Complete! ✅")

    def apply_theme(self):
        if self.is_dark:
            self.setStyleSheet("""
                QDialog { background-color: #1E1E2F; color: white; }
                QTableWidget { 
                    background-color: #2A2A3D; 
                    color: #E0E0E0; 
                    gridline-color: #5C6BC0; 
                    font-size: 15px;
                    border: none;
                }
                QHeaderView::section { 
                    background-color: #3949AB; 
                    color: white; 
                    font-weight: bold;
                    padding: 8px;
                }
                QTableWidget::item { padding: 5px; }
                QLabel { color: #81D4FA; }
            """)
        else:
            self.setStyleSheet("""
                QDialog { background-color: #F5F5F5; color: black; }
                QTableWidget { 
                    background-color: white; 
                    color: black; 
                    gridline-color: #BDBDBD; 
                    font-size: 15px;
                }
                QHeaderView::section { 
                    background-color: #2196F3; 
                    color: white; 
                    font-weight: bold;
                    padding: 8px;
                }
                QLabel { color: #0D47A1; }
            """)

# ----------------- Main OTP Widget -----------------
class OTPWidget(QWidget):
    def __init__(self, parent_theme_is_dark=True):
        super().__init__()
        self.is_dark = parent_theme_is_dark
        self.last_steps = []
        self.last_mode = "Encrypt"
        self.last_lang = "MIXED"
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("One-Time Pad (OTP)")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        file_layout = QHBoxLayout()
        self.btn_load = QPushButton("📂 Load File")
        self.btn_save = QPushButton("💾 Save File")
        self.btn_load.clicked.connect(self.load_file)
        self.btn_save.clicked.connect(self.save_file)
        file_layout.addWidget(self.btn_load)
        file_layout.addWidget(self.btn_save)
        layout.addLayout(file_layout)

        layout.addWidget(QLabel("Input Text (Output language will match input language):"))
        self.txt_input = QTextEdit()
        self.txt_input.setPlaceholderText("Enter message... (e.g., Hello مرحبا)")
        self.txt_input.setFixedHeight(80)
        layout.addWidget(self.txt_input)

        layout.addWidget(QLabel("Key (Auto-generated based on Input Text language):"))
        key_layout = QHBoxLayout()
        self.txt_key = QTextEdit()
        self.txt_key.setPlaceholderText("Key will appear here...")
        self.txt_key.setFixedHeight(60)
        
        self.btn_gen_key = QPushButton("🎲 Generate Key")
        self.btn_gen_key.setFixedSize(140, 60)
        self.btn_gen_key.clicked.connect(self.generate_random_key)
        
        key_layout.addWidget(self.txt_key)
        key_layout.addWidget(self.btn_gen_key)
        layout.addLayout(key_layout)

        action_layout = QHBoxLayout()
        self.btn_encrypt = QPushButton("🔒 Encrypt")
        self.btn_decrypt = QPushButton("🔓 Decrypt")
        
        self.btn_encrypt.clicked.connect(self.run_encrypt)
        self.btn_decrypt.clicked.connect(self.run_decrypt)
        
        action_layout.addWidget(self.btn_encrypt)
        action_layout.addWidget(self.btn_decrypt)
        layout.addLayout(action_layout)

        layout.addWidget(QLabel("Output Result:"))
        self.txt_output = QTextEdit()
        self.txt_output.setReadOnly(True)
        self.txt_output.setFixedHeight(80)
        layout.addWidget(self.txt_output)

        self.btn_visualize = QPushButton("🎬 Visualize Steps")
        self.btn_visualize.clicked.connect(self.show_visualization)
        self.btn_visualize.setEnabled(False)
        self.btn_visualize.setStyleSheet("background-color: #E91E63; color: white; font-weight: bold; font-size: 16px; padding: 12px;")
        layout.addWidget(self.btn_visualize)

        self.apply_styles()

    def generate_random_key(self):
        text = self.txt_input.toPlainText()
        text_len = len(text)
        if text_len == 0:
            QMessageBox.warning(self, "Warning", "Please enter input text first.")
            return
        
        key = OTPLogic.generate_key(text_len, text)
        self.txt_key.setText(key)
        
        _, lang = OTPLogic._get_alphabet(text)
        QMessageBox.information(self, "Key Generated", f"Key generated using the **{lang}** alphabet. (Input text was normalized to match the alphabet.)")


    def run_encrypt(self):
        text = self.txt_input.toPlainText()
        key = self.txt_key.toPlainText()
        
        if not text or not key:
            QMessageBox.warning(self, "Missing Info", "Please enter text and key.")
            return

        res, steps, lang = OTPLogic.encrypt(text, key)
        
        if res is None:
            # res is None indicates an error, steps holds the error message
            QMessageBox.critical(self, "Error", steps)
            return
            
        self.txt_output.setText(res)
        self.last_steps = steps
        self.last_mode = "Encrypt"
        self.last_lang = lang
        self.btn_visualize.setEnabled(True)

    def run_decrypt(self):
        text = self.txt_input.toPlainText()
        key = self.txt_key.toPlainText()

        if not text or not key:
            QMessageBox.warning(self, "Missing Info", "Please enter text and key.")
            return
        
        res, steps, lang = OTPLogic.decrypt(text, key)
        
        if res is None:
            QMessageBox.critical(self, "Error", steps)
            return
            
        self.txt_output.setText(res)
        self.last_steps = steps
        self.last_mode = "Decrypt"
        self.last_lang = lang
        self.btn_visualize.setEnabled(True)

    def show_visualization(self):
        if not self.last_steps: return
        vis = OTPVisualizer(self.last_steps, mode=self.last_mode, is_dark=self.is_dark, lang=self.last_lang)
        vis.exec()

    def load_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open", "", "Text Files (*.txt)")
        if fname:
            try:
                with open(fname, 'r', encoding='utf-8') as f:
                    self.txt_input.setText(f.read())
            except: pass

    def save_file(self):
        if not self.txt_output.toPlainText(): return
        fname, _ = QFileDialog.getSaveFileName(self, "Save", "", "Text Files (*.txt)")
        if fname:
            try:
                with open(fname, 'w', encoding='utf-8') as f:
                    f.write(self.txt_output.toPlainText())
            except: pass

    def apply_styles(self):
        btn_style = "border-radius: 8px; padding: 10px; font-size: 14px; font-weight: bold;"
        if self.is_dark:
            self.setStyleSheet(f"""
                QWidget {{ background-color: #1E1E2F; color: #E0E0E0; }}
                QTextEdit {{ background-color: #2A2A3D; color: white; border: 2px solid #3949AB; border-radius: 8px; }}
                QPushButton {{ background-color: #3949AB; color: white; {btn_style} }}
                QPushButton:hover {{ background-color: #5C6BC0; }}
            """)
        else:
            self.setStyleSheet(f"""
                QWidget {{ background-color: #F5F5F5; color: black; }}
                QTextEdit {{ background-color: white; color: black; border: 2px solid #BDBDBD; border-radius: 8px; }}
                QPushButton {{ background-color: #2196F3; color: white; {btn_style} }}
                QPushButton:hover {{ background-color: #42A5F5; }}
            """)