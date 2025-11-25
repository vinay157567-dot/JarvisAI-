from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import platform
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFloatingActionButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivy.uix.camera import Camera
from kivy.clock import Clock
from kivy.graphics import Color, Line
import threading
import requests
import webbrowser
import os
import time
from gtts import gTTS
from kivy.core.audio import SoundLoader

# --- CONFIGURATION ---
API_KEY = "AIzaSyCR25wftYhpZWtV5R8OSRhpCLuQCRUoKwQ"

# --- ANDROID NATIVE SETUP ---
if platform == 'android':
    from jnius import autoclass, cast
    from android.permissions import request_permissions, Permission
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    CurrentActivity = cast('android.app.Activity', PythonActivity.mActivity)
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')
    RecognizerIntent = autoclass('android.speech.RecognizerIntent')

# --- UI DESIGN (IRON MAN HUD) ---
KV = '''
ScreenManager:
    MainScreen:

<MainScreen>:
    name: "main"
    FloatLayout:
        # Black Background
        canvas.before:
            Color:
                rgba: 0, 0, 0, 1
            Rectangle:
                pos: self.pos
                size: self.size

        # CAMERA LAYER (Full Screen)
        Camera:
            id: camera_preview
            resolution: (640, 480)
            play: True
            allow_stretch: True
            keep_ratio: False

        # HUD OVERLAY (Graphics)
        Image:
            source: "assets/hud.png" # Agar image na ho to error na de isliye code se draw karenge
            opacity: 0

        # CENTER CIRCLE (Arc Reactor Style)
        MDIconButton:
            icon: "circle-outline"
            icon_size: "150sp"
            pos_hint: {"center_x": 0.5, "center_y": 0.5}
            theme_text_color: "Custom"
            text_color: 0, 1, 1, 0.6

        # HEADER
        MDLabel:
            text: "JARVIS: ONLINE"
            halign: "center"
            pos_hint: {"top": 0.95}
            bold: True
            font_style: "H5"
            theme_text_color: "Custom"
            text_color: 0, 1, 1, 1

        # CHAT TEXT DISPLAY
        MDLabel:
            id: chat_display
            text: "Tap Mic to Command..."
            halign: "center"
            pos_hint: {"center_y": 0.2}
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            font_style: "H6"
            bold: True

        # MIC BUTTON
        MDFloatingActionButton:
            icon: "microphone"
            icon_size: "40sp"
            md_bg_color: 1, 0, 0, 1
            pos_hint: {"center_x": 0.5, "y": 0.05}
            on_release: app.start_listening()
            
        # FLIP CAMERA BUTTON
        MDIconButton:
            icon: "camera-flip"
            icon_size: "40sp"
            pos_hint: {"right": 0.95, "top": 0.95}
            theme_text_color: "Custom"
            text_color: 0, 1, 1, 1
            on_release: app.flip_camera()
'''

class JarvisApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Cyan"
        return Builder.load_string(KV)

    def on_start(self):
        if platform == 'android':
            request_permissions([
                Permission.RECORD_AUDIO, 
                Permission.INTERNET, 
                Permission.CALL_PHONE,
                Permission.CAMERA
            ])

    def flip_camera(self):
        cam = self.root.get_screen('main').ids.camera_preview
        cam.play = False
        cam.index = 1 if cam.index == 0 else 0
        cam.play = True

    def start_listening(self):
        if platform == 'android':
            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "hi-IN")
            try: CurrentActivity.startActivityForResult(intent, 100)
            except: self.root.get_screen('main').ids.chat_display.text = "Mic Error"
        else:
            self.process_command("open youtube")

    def on_activity_result(self, requestCode, resultCode, intent):
        if requestCode == 100:
            matches = intent.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            if matches and matches.size() > 0:
                text = matches.get(0)
                self.root.get_screen('main').ids.chat_display.text = f"You: {text}"
                self.process_command(text)

    def process_command(self, text):
        text = text.lower()
        
        # --- AUTOMATION COMMANDS ---
        if "open youtube" in text:
            self.speak("Opening YouTube Boss")
            self.open_url("https://youtube.com")
            return
        if "open whatsapp" in text:
            self.speak("Opening WhatsApp")
            self.open_url("whatsapp://")
            return
        if "open facebook" in text:
            self.speak("Opening Facebook")
            self.open_url("https://facebook.com")
            return
            
        # --- AI BRAIN ---
        threading.Thread(target=self.ask_gemini, args=(text,)).start()

    def open_url(self, url):
        if platform == 'android':
            intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
            try: CurrentActivity.startActivity(intent)
            except: webbrowser.open(url)
        else: webbrowser.open(url)

    def ask_gemini(self, text):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": text}]}],
                "systemInstruction": {"parts": [{"text": "You are JARVIS. Reply shortly in Hindi/English."}]}
            }
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                reply = response.json()['candidates'][0]['content']['parts'][0]['text'].replace("*", "")
                Clock.schedule_once(lambda dt: self.update_ui(reply))
                self.speak(reply)
        except: pass

    def update_ui(self, text):
        self.root.get_screen('main').ids.chat_display.text = text

    def speak(self, text):
        threading.Thread(target=self._speak_thread, args=(text,)).start()

    def _speak_thread(self, text):
        try:
            path = os.path.join(self.user_data_dir, 'speech.mp3')
            if os.path.exists(path): os.remove(path)
            tts = gTTS(text=text[:200], lang='hi')
            tts.save(path)
            SoundLoader.load(path).play()
        except: pass

if __name__ == "__main__":
    if platform == 'android':
        from android import activity
        activity.bind(on_activity_result=JarvisApp().on_activity_result)
    JarvisApp().run()
