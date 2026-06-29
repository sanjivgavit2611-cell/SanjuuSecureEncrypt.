import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window

# Back-end core script se cryptographic functions ko import karna
from main import encrypt_sse_u1, decrypt_sse_u1, get_or_create_rsa_keys

# JADUI LINE: Keyboard aate hi window ko automatic adjust/resize karna
Window.softinput_mode = 'resize'
Window.clearcolor = (0.04, 0.04, 0.06, 1)

class SSEU1ProductionWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Main layout hamesha vertical rahega
        self.orientation = 'vertical'

        # Background mein RSA keys ko ready rakhna
        self.private_key, self.public_key = get_or_create_rsa_keys()

        # 1. FIXED HEADER: Yeh top par hamesha dikhta rahega, scroll nahi hoga
        self.status_label = Label(
            text="🔒 SSE-U1 CRYPTO VAULT",
            font_size='22sp',
            bold=True,
            color=(0, 0.8, 1, 1),
            size_hint_y=None,
            height=100
        )
        self.add_widget(self.status_label)

        # 2. SCROLL CONTAINER: Iske andar ka maal scroll ho sakega
        scroll_view = ScrollView()
        
        # Grid layout jo scroll view ke andar saare input control widgets hold karega
        content_layout = GridLayout(cols=1, spacing=15, size_hint_y=None)
        content_layout.padding = [40, 20, 40, 40]
        
        # Yeh line container ki height ko content ke hisab se dynamic badalti hai
        content_layout.bind(minimum_height=content_layout.setter('height'))

        # 3. Input Component: Target Filename
        content_layout.add_widget(Label(text="Target Filename:", font_size='14sp', size_hint_y=None, height=30))
        self.file_input = TextInput(
            text="payload.txt",
            multiline=False,
            font_size='16sp',
            size_hint_y=None,
            height=90
        )
        content_layout.add_widget(self.file_input)

        # 4. Input Component: Master Password
        content_layout.add_widget(Label(text="Master Secret Password:", font_size='14sp', size_hint_y=None, height=30))
        self.password_input = TextInput(
            multiline=False,
            password=True,
            font_size='16sp',
            size_hint_y=None,
            height=90
        )
        content_layout.add_widget(self.password_input)

        # Space gap
        content_layout.add_widget(Label(size_hint_y=None, height=10))

        # 5. Action Button: ENCRYPT
        self.encrypt_btn = Button(
            text="🔒 SECURE & PACK (.sseu1)",
            font_size='16sp',
            bold=True,
            background_color=(0, 0.6, 0.2, 1),
            size_hint_y=None,
            height=110
        )
        self.encrypt_btn.bind(on_press=self.trigger_encryption)
        content_layout.add_widget(self.encrypt_btn)

        # 6. Action Button: DECRYPT
        self.decrypt_btn = Button(
            text="🔓 UNPACK & RECOVER",
            font_size='16sp',
            bold=True,
            background_color=(0.7, 0.1, 0.1, 1),
            size_hint_y=None,
            height=110
        )
        self.decrypt_btn.bind(on_press=self.trigger_decryption)
        content_layout.add_widget(self.decrypt_btn)

        # Saare content ko scroll view mein daalna aur use main window mein add karna
        scroll_view.add_widget(content_layout)
        self.add_widget(scroll_view)

    def trigger_encryption(self, instance):
        filename = self.file_input.text.strip()
        password = self.password_input.text.strip()

        if not filename or not password:
            self.update_status("❌ Error: Missing Fields!", (1, 0, 0, 1))
            return

        if not os.path.exists(filename):
            self.update_status(f"🚨 File '{filename}' not found!", (1, 0.5, 0, 1))
            return

        try:
            encrypt_sse_u1(filename, "secure_data.sseu1", password, self.public_key)
            self.update_status("✓ Packaged into 'secure_data.sseu1'!", (0, 1, 0, 1))
        except Exception as e:
            self.update_status(f"🚨 Engine Error: {str(e)[:20]}", (1, 0, 0, 1))

    def trigger_decryption(self, instance):
        password = self.password_input.text.strip()

        if not password:
            self.update_status("❌ Password required!", (1, 0, 0, 1))
            return

        try:
            decrypt_sse_u1("secure_data.sseu1", "recovered_gui_data.txt", password, self.private_key)
            self.update_status("🔒 Success! Decrypted data saved.", (0, 1, 0, 1))
        except Exception as e:
            self.update_status("🚨 Tampering or Wrong Password!", (1, 0, 0, 1))

    def update_status(self, message, color):
        self.status_label.text = message
        self.status_label.color = color


class SSEU1App(App):
    def build(self):
        self.title = "SSE-U1 Responsive Suite"
        return SSEU1ProductionWindow()

if __name__ == '__main__':
    SSEU1App().run()
