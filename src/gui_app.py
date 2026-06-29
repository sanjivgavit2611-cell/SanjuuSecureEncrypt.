import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.core.window import Window

# Back-end script se core algorithms lana
from main import encrypt_sse_u1, decrypt_sse_u1, get_or_create_rsa_keys

Window.softinput_mode = 'resize'
Window.clearcolor = (0.04, 0.04, 0.06, 1)

class SSEU1ProductionWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        # Background RSA keys load/generate karna
        self.private_key, self.public_key = get_or_create_rsa_keys()

        # 1. FIXED HEADER
        self.status_label = Label(
            text="🔒 SSE-U1 CRYPTO VAULT",
            font_size='22sp',
            bold=True,
            color=(0, 0.8, 1, 1),
            size_hint_y=None,
            height=100
        )
        self.add_widget(self.status_label)

        # 2. SCROLL VIEW CONTAINER
        scroll_view = ScrollView()
        content_layout = GridLayout(cols=1, spacing=15, size_hint_y=None)
        content_layout.padding = [40, 20, 40, 40]
        content_layout.bind(minimum_height=content_layout.setter('height'))

        # 3. Component: Selected File Display & Browse Button
        content_layout.add_widget(Label(text="Selected Target File:", font_size='14sp', size_hint_y=None, height=30))
        
        # Horizontal layout file input aur browse button ko sath rakhne ke liye
        file_selection_box = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=90)
        
        self.file_input = TextInput(
            text="payload.txt",
            multiline=False,
            font_size='14sp',
            readonly=True # User ab isme khud type nahi karega, sirf touch se select karega
        )
        file_selection_box.add_widget(self.file_input)
        
        # BROWSE BUTTON
        browse_btn = Button(
            text="BROWSE",
            font_size='14sp',
            bold=True,
            background_color=(0, 0.5, 1, 1), # Neon Blue
            size_hint_x=None,
            width=200
        )
        browse_btn.bind(on_press=self.open_file_chooser)
        file_selection_box.add_widget(browse_btn)
        
        content_layout.add_widget(file_selection_box)

        # 4. Component: Master Password Input
        content_layout.add_widget(Label(text="Master Secret Password:", font_size='14sp', size_hint_y=None, height=30))
        self.password_input = TextInput(
            multiline=False,
            password=True,
            font_size='16sp',
            size_hint_y=None,
            height=90
        )
        content_layout.add_widget(self.password_input)

        content_layout.add_widget(Label(size_hint_y=None, height=10))

        # 5. Encryption Button
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

        # 6. Decryption Button
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

        scroll_view.add_widget(content_layout)
        self.add_widget(scroll_view)

    def open_file_chooser(self, instance):
        """File select karne ke liye ek visual popup kholta hai."""
        # Popup ka main layout
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Kivy ka File Chooser list layout
        # path='.' ka matlab hai yeh hamare project ke folder se shuru hoga
        self.file_chooser = FileChooserListView(path='.')
        popup_layout.add_widget(self.file_chooser)
        
        # Select Button inside popup
        select_btn = Button(text="SELECT FILE", size_hint_y=None, height=100, bold=True, background_color=(0, 0.8, 1, 1))
        popup_layout.add_widget(select_btn)
        
        # Popup Window instantiate karna
        self.popup = Popup(title="Select File to Process", content=popup_layout, size_hint=(0.9, 0.9))
        
        # Select button dabane par file uthane ka event bind karna
        select_btn.bind(on_press=self.confirm_file_selection)
        
        self.popup.open()

    def confirm_file_selection(self, instance):
        """User ne jo file chuni hai use main box mein text field par daalna."""
        selected = self.file_chooser.selection
        if selected:
            # Full path se sirf file ka naam nikalna (e.g., 'payload.txt')
            filename_only = os.path.basename(selected[0])
            self.file_input.text = filename_only
        self.popup.dismiss() # Popup window ko band kar dena

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
        filename = self.file_input.text.strip()
        password = self.password_input.text.strip()

        if not password:
            self.update_status("❌ Password required!", (1, 0, 0, 1))
            return

        try:
            # Agar user ne .sseu1 select kiya hai toh theek, warna default package uthayega
            package_name = filename if filename.endswith('.sseu1') else "secure_data.sseu1"
            decrypt_sse_u1(package_name, "recovered_gui_data.txt", password, self.private_key)
            self.update_status("🔒 Success! Decrypted data saved.", (0, 1, 0, 1))
        except Exception as e:
            self.update_status("🚨 Tampering or Wrong Password!", (1, 0, 0, 1))

    def update_status(self, message, color):
        self.status_label.text = message
        self.status_label.color = color


class SSEU1App(App):
    def build(self):
        self.title = "SSE-U1 Visual Suite"
        return SSEU1ProductionWindow()

if __name__ == '__main__':
    SSEU1App().run()
