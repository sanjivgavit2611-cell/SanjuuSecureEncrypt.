[app]
# App ka naam jo screen par dikhega
title = SSE Vault

# Package details
package.name = sse_vault
package.domain = org.sanjuu

# Source directories (jahan hamara code hai)
source.dir = src
source.include_exts = py, png, jpg, kv, pem

# Application version
version = 1.0.0

# Application requirements (Hamari libraries jo app ko chahiye)
requirements = python3, kivy==2.3.0, pycryptodome, argon2-cffi, cffi

# Orientation setup
orientation = portrait

# Android specific settings
osx.kivy_version = 2.3.0
fullscreen = 0
android.archs = arm64-v8a

# Kivy ko batana ki hamari main file gui_app.py hai
# (Buildozer default mein main.py dhoondta hai, isliye hum isse override kar rahe hain)
android.entrypoint = gui_app.py
