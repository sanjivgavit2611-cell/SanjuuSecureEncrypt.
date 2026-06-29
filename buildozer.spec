[app]
title = SSE Vault
package.name = sse_vault
package.domain = org.sanjuu
source.dir = src
source.include_exts = py, png, jpg, kv, pem
version = 1.0.0

# JADUI COMBINATION: Pinned version hataya aur pyjnius ko include kiya
requirements = python3, kivy, pyjnius, pycryptodome, argon2-cffi, cffi

orientation = portrait
fullscreen = 0

# STABLE ANDROID SETTINGS
android.api = 34
android.minapi = 21
android.ndk = 26b
android.ndk_api = 21
android.archs = arm64-v8a
android.entrypoint = gui_app.py
