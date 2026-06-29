import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window

# Back-end core script se cryptographic functions ko import karna
from main import encrypt_sse_u1, decrypt_sse_u1, get_or_create_rsa_keys

# Dark Cyberpunk background color
Window.clearcolor = (0.04, 0.04, 0.06, 1)

class SSEU1ProductionWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [40, 40, 40, 40]
        self.spacing = 15

        # Background mein RSA keys ko ready kar lena (V2 feature)
        self.private_key, self.public_key = get_or_create_rsa_keys()

        # 1. Main Header Title
        self.status_label = Label(
            text="🔒 SSE-U1 CRYPTO VAULT",
            font_size='24sp',
            bold=True,
            color=(0, 0.8, 1, 1), # Cyan Neon
            size_hint_y=None,
            height=80
        )
        self.add_widget(self.status_label)

        # 2. Input Box: Target Filename
        self.add_widget(Label(text="Target Filename (e.g., payload.txt):", font_size='14sp', size_hint_y=None, height=30))
        self.file_input = TextInput(
            text="payload.txt", # Default text testing ke liye
            multiline=False,
            font_size='16sp',
            size_hint_y=None,
            height=90
        )
        self.add_widget(self.file_input)

        # 3. Input Box: Master Password
        self.add_widget(Label(text="Master Secret Password:", font_size='14sp', size_hint_y=None, height=30))
        self.password_input = TextInput(
            multiline=False,
            password=True, # Password hides with dots
            font_size='16sp',
            size_hint_y=None,
            height=90
        )
        self.add_widget(self.password_input)

        # Space gap dene ke liye empty widget divider
        self.add_widget(Label(size_hint_y=None, height=10))

        # 4. Action Button: ENCRYPT
        self.encrypt_btn = Button(
            text="🔒 SECURE & PACK (.sseu1)",
            font_size='16sp',
            bold=True,
            background_color=(0, 0.6, 0.2, 1), # Green Neon
            size_hint_y=None,
            height=110
        )
        self.encrypt_btn.bind(on_press=self.trigger_encryption)
        self.add_widget(self.encrypt_btn)

        # 5. Action Button: DECRYPT
        self.decrypt_btn = Button(
            text="🔓 UNPACK & RECOVER",
            font_size='16sp',
            bold=True,
            background_color=(0.7, 0.1, 0.1, 1), # Red Neon
            size_hint_y=None,
            height=110
        )
        self.decrypt_btn.bind(on_press=self.trigger_decryption)
        self.add_widget(self.decrypt_btn)

    def trigger_encryption(self, instance):
        """Asli core encryption logic ko back-end par run karta hai."""
        filename = self.file_input.text.strip()
        password = self.password_input.text.strip()

        if not filename or not password:
            self.update_status("❌ Error: Missing Fields!", (1, 0, 0, 1))
            return

        if not os.path.exists(filename):
            self.update_status(f"🚨 File '{filename}' not found!", (1, 0.5, 0, 1))
            return

        try:
            # main.py ka function call ho raha hai yahan!
            encrypt_sse_u1(filename, "secure_data.sseu1", password, self.public_key)
            self.update_status(f"✓ Packaged into 'secure_data.sseu1'!", (0, 1, 0, 1))
        except Exception as e:
            self.update_status(f"🚨 Engine Error: {str(e)[:20]}", (1, 0, 0, 1))

    def trigger_decryption(self, instance):
        """Asli core decryption logic ko execute karta hai."""
        filename = self.file_input.text.strip() # Isme package file ka naam aayega
        password = self.password_input.text.strip()

        if not password:
            self.update_status("❌ Password required!", (1, 0, 0, 1))
            return

        try:
            # Custom unpack operation execution
            decrypt_sse_u1("secure_data.sseu1", "recovered_gui_data.txt", password, self.private_key)
            self.update_status("🔒 Success! Decrypted to 'recovered_gui_data.txt'", (0, 1, 0, 1))
        except Exception as e:
            self.update_status("🚨 Tampering or Wrong Password!", (1, 0, 0, 1))

    def update_status(self, message, color):
        """Top label ka text aur color dynamically change karne ke liye helper."""
        self.status_label.text = message
        self.status_label.color = color


class SSEU1App(App):
    def build(self):
        self.title = "SSE-U1 Professional Suite"
        return SSEU1ProductionWindow()

if __name__ == '__main__':
    SSEU1App().run()
