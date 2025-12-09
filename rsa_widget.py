import re
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QTextEdit, QFrame,
                               QFileDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

import rsa_logic


class RSAPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.e_is_system = False
        self.d_is_system = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title
        title = QLabel("RSA Implementation")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Keys Frame
        keys_frame = QFrame()
        keys_frame.setStyleSheet("background-color: rgba(0,0,0,0.05); border-radius: 10px; padding: 8px;")
        keys_layout = QVBoxLayout(keys_frame)

        # Row 1: Primes
        row1 = QHBoxLayout()
        self.p_input = self.create_input("p (Prime 1):", "Generate or enter")
        self.q_input = self.create_input("q (Prime 2):", "Generate or enter")
        row1.addLayout(self.p_input)
        row1.addLayout(self.q_input)
        keys_layout.addLayout(row1)

        # Row 2: Keys e, d
        row2 = QHBoxLayout()
        self.e_input = self.create_input("e (Public):", "Optional / Auto")
        self.d_input = self.create_input("d (Private):", "Optional / Auto")

        self.e_input.widget_ref.textEdited.connect(lambda: self.set_user_flag('e'))
        self.d_input.widget_ref.textEdited.connect(lambda: self.set_user_flag('d'))

        row2.addLayout(self.e_input)
        row2.addLayout(self.d_input)
        keys_layout.addLayout(row2)

        # Row 3: N (Modulus)
        row3 = QHBoxLayout()
        self.n_input = self.create_input("n (Modulus):", "Auto-calculated OR Paste here for Decrypt")
        self.n_input.widget_ref.setStyleSheet("background-color: #E3F2FD; color: #000; font-weight: bold;")
        row3.addLayout(self.n_input)
        keys_layout.addLayout(row3)

        # Generate Button
        self.gen_btn = QPushButton("Generate / Validate Keys")
        self.gen_btn.setFixedHeight(40)
        self.gen_btn.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; font-size: 14px;")
        self.gen_btn.clicked.connect(self.handle_keys)
        keys_layout.addWidget(self.gen_btn)

        layout.addWidget(keys_frame)

        # Message Input + Import buttons
        text_row = QHBoxLayout()
        self.msg_input = QTextEdit()
        self.msg_input.setPlaceholderText("Enter Plain text (to Encrypt) OR Cipher text (to Decrypt)...")
        self.msg_input.setMaximumHeight(120)
        text_row.addWidget(self.msg_input)

        import_col = QVBoxLayout()
        self.import_text_btn = QPushButton("Import Text File")
        self.import_text_btn.clicked.connect(self.import_text_file)
        self.import_cipher_btn = QPushButton("Import Cipher File")
        self.import_cipher_btn.clicked.connect(self.import_cipher_file)
        import_col.addWidget(self.import_text_btn)
        import_col.addWidget(self.import_cipher_btn)
        text_row.addLayout(import_col)

        layout.addLayout(text_row)

        # Action Buttons
        btn_row = QHBoxLayout()
        self.enc_btn = QPushButton("Encrypt & Show Steps")
        self.enc_btn.clicked.connect(self.run_encrypt)
        self.dec_btn = QPushButton("Decrypt & Show Steps")
        self.dec_btn.clicked.connect(self.run_decrypt)

        for btn in [self.enc_btn, self.dec_btn]:
            btn.setFixedHeight(45)
            btn.setStyleSheet("font-size: 14px; font-weight: bold;")
            btn_row.addWidget(btn)

        # Export buttons
        self.export_cipher_btn = QPushButton("Export Result")
        self.export_cipher_btn.setFixedHeight(45)
        self.export_cipher_btn.clicked.connect(self.export_result_file)
        btn_row.addWidget(self.export_cipher_btn)

        layout.addLayout(btn_row)

        # Output
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setPlaceholderText("Results will appear here...")
        self.output_area.setMinimumHeight(160)
        layout.addWidget(self.output_area)

        # Connect live validators
        for layout_obj in [self.p_input, self.q_input, self.e_input, self.d_input, self.n_input]:
            layout_obj.widget_ref.textEdited.connect(self.validate_inputs)

        # initial validation state
        self.validate_inputs()

    def create_input(self, label_text, placeholder):
        l = QVBoxLayout()
        lbl = QLabel(label_text)
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        l.addWidget(lbl)
        l.addWidget(inp)
        l.widget_ref = inp
        return l

    def set_user_flag(self, key_type):
        if key_type == 'e': self.e_is_system = False
        elif key_type == 'd': self.d_is_system = False

    def get_val(self, layout_obj):
        text = layout_obj.widget_ref.text().strip()
        if not text: return None
        try:
            return int(text)
        except ValueError:
            return "Error"

    # ---------------------- Live validation ----------------------
    def set_field_ok(self, layout_obj, ok):
        if ok:
            layout_obj.widget_ref.setStyleSheet("")
        else:
            layout_obj.widget_ref.setStyleSheet("border: 2px solid #e53935; background: #ffebee;")

    def validate_inputs(self):
        # Validate p and q as primes
        p_val = self.get_val(self.p_input)
        q_val = self.get_val(self.q_input)
        e_val = self.get_val(self.e_input)
        d_val = self.get_val(self.d_input)
        n_val = self.get_val(self.n_input)

        p_ok = (p_val is None) or (isinstance(p_val, int) and rsa_logic.is_prime(p_val))
        q_ok = (q_val is None) or (isinstance(q_val, int) and rsa_logic.is_prime(q_val))
        e_ok = (e_val is None) or (isinstance(e_val, int) and e_val > 1)
        d_ok = (d_val is None) or (isinstance(d_val, int) and d_val > 1)
        n_ok = (n_val is None) or (isinstance(n_val, int) and n_val > 0)

        self.set_field_ok(self.p_input, p_ok)
        self.set_field_ok(self.q_input, q_ok)
        self.set_field_ok(self.e_input, e_ok)
        self.set_field_ok(self.d_input, d_ok)
        self.set_field_ok(self.n_input, n_ok)

        # Determine whether encrypt/decrypt buttons should be enabled
        can_encrypt = (n_val is not None and isinstance(n_val, int) and e_val is not None and isinstance(e_val, int))
        can_decrypt = (n_val is not None and isinstance(n_val, int) and d_val is not None and isinstance(d_val, int))

        self.enc_btn.setEnabled(bool(can_encrypt))
        self.dec_btn.setEnabled(bool(can_decrypt))
        self.export_cipher_btn.setEnabled(False)  # becomes True after result exists

        # short status in output_area (non-intrusive)
        status_msgs = []
        if not p_ok:
            status_msgs.append("p is not a valid prime")
        if not q_ok:
            status_msgs.append("q is not a valid prime")
        if not e_ok and self.e_input.widget_ref.text().strip():
            status_msgs.append("e looks invalid")
        if not d_ok and self.d_input.widget_ref.text().strip():
            status_msgs.append("d looks invalid")

        if status_msgs:
            self.output_area.setPlainText("Validation: " + "; ".join(status_msgs))
        else:
            # keep previous results if any, don't erase
            pass

    # ---------------------- Key handling ----------------------
    def handle_keys(self):
        try:
            p = self.get_val(self.p_input)
            q = self.get_val(self.q_input)
            e_val = self.get_val(self.e_input)
            d_val = self.get_val(self.d_input)

            if p == "Error" or q == "Error": raise ValueError("P and Q must be integers.")
            if p is None or q is None: raise ValueError("P and Q are mandatory for generation.")

            final_e, final_d = e_val, d_val
            if self.e_is_system: final_e = None
            if self.d_is_system: final_d = None

            e_final, n_final, d_final = rsa_logic.complete_keys(p, q, final_e, final_d)

            # تحديث الواجهة بما في ذلك مربع n
            self.n_input.widget_ref.setText(str(n_final))

            self.e_input.widget_ref.setText(str(e_final))
            if final_e is None: self.e_is_system = True

            self.d_input.widget_ref.setText(str(d_final))
            if final_d is None: self.d_is_system = True

            status = "Arabic Supported" if n_final > 2000 else "English Only"
            self.output_area.setHtml(f"✅ Keys Ready!<br>Status: {status}<br><br>Using:<br>n = {n_final}<br>e = {e_final}<br>d = {d_final}")

            # revalidate
            self.validate_inputs()

        except Exception as err:
            self.output_area.setText(f"❌ Key Generation Error:\n{str(err)}")

    # ---------------------- Import / Export ----------------------
    def import_text_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Text File", "", "Text Files (*.txt);;All Files (*)")
        if not path:
            return
        try:
            content = rsa_logic.load_text_file(path)
            self.msg_input.setPlainText(content)
            self.output_area.setPlainText(f"Imported text from: {path}")
        except Exception as e:
            self.output_area.setPlainText(f"Failed to import file: {e}")

    def import_cipher_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Cipher File", "", "Text Files (*.txt);;All Files (*)")
        if not path:
            return
        try:
            content = rsa_logic.load_text_file(path)
            text = content.replace('\r\n', '\n')

            cipher_block = None
            keys_block = None

            # Try to locate the exact user-produced sections first
            m_cipher_header = re.search(r"🔒\s*Cipher Result\s*:?", text, re.IGNORECASE)
            m_keys_header = re.search(r"🔑\s*Save these for Decryption\s*:?", text, re.IGNORECASE)

            if m_cipher_header and m_keys_header and m_keys_header.start() > m_cipher_header.end():
                # cipher is between the two headers
                cipher_block = text[m_cipher_header.end(): m_keys_header.start()].strip()
                # keys block starts at keys_header end and ends at next header (like Decryption Formula) or blank line
                rest_after_keys = text[m_keys_header.end():]
                m_next_header = re.search(r"\n\s*Decryption Formula:|\n\s*-{3,}|\n\s*$", rest_after_keys, re.IGNORECASE)
                if m_next_header:
                    keys_block = rest_after_keys[:m_next_header.start()].strip()
                else:
                    keys_block = rest_after_keys.strip()

            elif m_cipher_header:
                # found cipher header but not keys header nearby: take lines after header up to first blank line
                rest = text[m_cipher_header.end():]
                m_blank = re.search(r"\n\s*\n", rest)
                if m_blank:
                    cipher_block = rest[:m_blank.start()].strip()
                else:
                    cipher_block = rest.strip()

            else:
                # no special headers found — fall back to finding any integer tokens in the entire file
                try:
                    nums = rsa_logic.parse_cipher_string(text)
                    cipher_block = ", ".join(str(x) for x in nums)
                except Exception:
                    cipher_block = text

            # Extract d and n from keys_block if present; otherwise try a global search but prefer the keys_block
            d_val = None
            n_val = None
            if keys_block:
                d_match = re.search(r"\bd\s*[:=]\s*(\d+)\b", keys_block, re.IGNORECASE)
                n_match = re.search(r"\bn\s*[:=]\s*(\d+)\b", keys_block, re.IGNORECASE)
            else:
                d_match = re.search(r"\bd\s*[:=]\s*(\d+)\b", text, re.IGNORECASE)
                n_match = re.search(r"\bn\s*[:=]\s*(\d+)\b", text, re.IGNORECASE)

            extracted = []
            if d_match:
                d_val = d_match.group(1)
                self.d_input.widget_ref.setText(d_val)
                extracted.append(f"d={d_val}")
            if n_match:
                n_val = n_match.group(1)
                self.n_input.widget_ref.setText(n_val)
                extracted.append(f"n={n_val}")

            # Normalize and place cipher into msg_input using the robust parser
            try:
                nums = rsa_logic.parse_cipher_string(cipher_block)
                cipher_text = ", ".join(str(x) for x in nums)
                self.msg_input.setPlainText(cipher_text)
            except Exception:
                self.msg_input.setPlainText(cipher_block)

            if extracted:
                self.output_area.setPlainText(f"Imported cipher from: {path} — extracted: {', '.join(extracted)}")
            else:
                self.output_area.setPlainText(f"Imported cipher from: {path} — no keys found in file")

            # re-validate inputs after filling fields
            self.validate_inputs()

            # Auto-decrypt only for files in the expected format (we extracted both d and n)
            if d_val and n_val:
                try:
                    d_int = int(d_val)
                    n_int = int(n_val)

                    # small-n warning
                    warn_prefix = ""
                    if n_int < 2000:
                        warn_prefix = "⚠️ Warning: The modulus n is small and not secure for real use.\n\n"

                    # Attempt decryption using the parser result (msg_input currently has a normalized list like "44, 45, ...")
                    plain, steps = rsa_logic.rsa_decrypt_with_steps(self.msg_input.toPlainText(), d_int, n_int)

                    # Display auto-decrypted result (include warning if applicable)
                    self.output_area.setHtml(
                        warn_prefix +
                        f"🔓 <b>Auto-Decrypted Message:</b><br>"
                        f"<span style='font-size:18px; color:#4CAF50'>{plain}</span><br><br>"
                        f"📝 <b>Decryption Steps:</b><br><pre>{steps}</pre>"
                    )
                    self.export_cipher_btn.setEnabled(True)

                except Exception as e:
                    # If auto-decrypt fails, keep a clear message but don't raise
                    self.output_area.setPlainText(f"Imported cipher from: {path} — extracted: {', '.join(extracted)}\nAuto-decrypt failed: {e}")

        except Exception as e:
            self.output_area.setPlainText(f"Failed to import cipher file: {e}")

    def export_result_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Result", "result.txt", "Text Files (*.txt);;All Files (*)")
        if not path:
            return
        try:
            content = self.output_area.toPlainText()
            rsa_logic.save_text_file(path, content)
            self.output_area.setPlainText(f"Saved result to: {path}")
        except Exception as e:
            self.output_area.setPlainText(f"Failed to save result: {e}")

    # ---------------------- Encrypt / Decrypt ----------------------
    def run_encrypt(self):
        try:
            n = self.get_val(self.n_input)
            e = self.get_val(self.e_input)

            if n is None or e is None or n == "Error" or e == "Error":
                raise ValueError("For Encryption, you need 'n' and 'e'. Please generate keys or fill them.")

            text = self.msg_input.toPlainText()
            if not text:
                return

            cipher, steps = rsa_logic.rsa_encrypt_with_steps(text, e, n)

            # جلب d للعرض فقط
            d_display = self.d_input.widget_ref.text()

            display = (
                f"🔒 <b>Cipher Result:</b><br>"
                f"<span style='font-size:16px; color:#E91E63'>{cipher}</span><br><br>"
                f"🔑 <b>Save these for Decryption:</b><br>"
                f"d = {d_display}<br>n = {n}<br><br>"
                f"📝 <b>Encryption Steps:</b><br><pre>{steps}</pre>"
            )
            self.output_area.setHtml(display)
            self.export_cipher_btn.setEnabled(True)

        except Exception as err:
            self.output_area.setText(f"Encryption Error: {str(err)}")

    def run_decrypt(self):
        try:
            n = self.get_val(self.n_input)
            d = self.get_val(self.d_input)

            if n is None or d is None or n == "Error" or d == "Error":
                raise ValueError("For Decryption, you MUST enter 'n' and 'd' in the boxes above.")

            cipher = self.msg_input.toPlainText()
            if not cipher:
                return

            # Use the robust parser inside rsa_decrypt_with_steps
            plain, steps = rsa_logic.rsa_decrypt_with_steps(cipher, d, n)

            self.output_area.setHtml(
                f"🔓 <b>Decrypted Message:</b><br>"
                f"<span style='font-size:18px; color:#4CAF50'>{plain}</span><br><br>"
                f"📝 <b>Decryption Steps:</b><br>"
                f"<pre>{steps}</pre>"
            )
            self.export_cipher_btn.setEnabled(True)

        except Exception as err:
            self.output_area.setText(f"Decryption Error: {str(err)}")
