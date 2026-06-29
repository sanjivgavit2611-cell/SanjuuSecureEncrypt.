[app]
title = SSE Vault
package.name = sse_vault
package.domain = org.sanjuu
source.dir = src
source.include_exts = py, png, jpg, kv, pem
version = 1.0.0

# Sab kuch exactly pinned hai
requirements = python3, kivy==2.3.0, pycryptodome, argon2-cffi, cffi

orientation = portrait
fullscreen = 0

# STABLE ANDROID SETTINGS (NDK 25b is universally most stable for C-extensions)
android.api = 34
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a
android.entrypoint = gui_app.py

# Internet se download rokne ke liye local stable folder ko force karna
p4a.source_dir = ./python-for-android
