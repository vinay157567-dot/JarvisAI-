[app]
title = Jarvis Pro
package.name = jarvis.pro
package.domain = org.vinay
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 2.0
Heavy Requirements for Camera & AI
requirements = python3,kivy==2.3.0,kivymd,requests,gtts,android,pyjnius,pillow
Permissions
android.permissions = INTERNET,RECORD_AUDIO,CALL_PHONE,CAMERA,WRITE_EXTERNAL_STORAGE
Android 14 Settings
android.api = 34
android.minapi = 24
android.accept_sdk_license = True
orientation = portrait
fullscreen = 1
[buildozer]
log_level = 2
warn_on_root = 1
