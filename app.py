"""
OCR overlay minimal avec lookup TM.
Usage local uniquement.
Installez Tesseract et configurez PATH si nécessaire.
"""
import time
import threading
from PIL import ImageGrab, Image
import pytesseract
import json
from pathlib import Path
import tkinter as tk

# Config
REGION = None  # None = full screen; or (left, top, right, bottom)
LANG = 'jpn'   # tesseract language pack, ex 'jpn' ou 'jpn+eng'
TM_PATH = Path(__file__).resolve().parents[1] / 'tm_manager' / 'sample_tm.json'
CAPTURE_INTERVAL = 1.0  # secondes

def load_tm():
    if TM_PATH.exists():
        try:
            return json.loads(TM_PATH.read_text(encoding='utf-8'))
        except Exception:
            return {}
    return {}

def ocr_capture():
    img = ImageGrab.grab(bbox=REGION)
    return img

def ocr_text_from_image(img):
    try:
        text = pytesseract.image_to_string(img, lang=LANG)
        return text.strip()
    except Exception:
        return ""

class OverlayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FGO Translation Helper - OCR Overlay")
        self.label = tk.Label(root, text="", justify='left', font=("Consolas", 10), bg='black', fg='white')
        self.label.pack(fill='both', expand=True)
        self.tm = load_tm()
        self.running = True
        self.update_loop()

    def lookup_translation(self, source):
        if not source:
            return ""
        # simple exact lookup
        return self.tm.get(source, "")

    def update_loop(self):
        def worker():
            while self.running:
                img = ocr_capture()
                text = ocr_text_from_image(img)
                # simple segmentation: split lines and lookup each
                lines = [l.strip() for l in text.splitlines() if l.strip()]
                out_lines = []
                for line in lines:
                    trans = self.lookup_translation(line)
                    if trans:
                        out_lines.append(f"{line} → {trans}")
                    else:
                        out_lines.append(line)
                display = "\n".join(out_lines)[:4000]
                # update UI in main thread
                self.label.after(0, self.label.config, {'text': display})
                time.sleep(CAPTURE_INTERVAL)
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def stop(self):
        self.running = False

def main():
    root = tk.Tk()
    app = OverlayApp(root)
    try:
        root.mainloop()
    finally:
        app.stop()

if __name__ == "__main__":
    main()
