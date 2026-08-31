import os
from tkinter import messagebox

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
except ImportError:
    messagebox.showerror("Error", "Please install required libraries: pip install arabic-reshaper python-bidi")
    exit()

def ar(text):
    """Helper function to reshape Arabic text and fix RTL direction"""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

# Base Paths Configuration
# We go one level up from `src/utils` to `src`, and another level up to `ModMakerCore`
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PACKS_DIR = os.path.join(BASE_DIR, "packs")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Ensure required directories exist
os.makedirs(PACKS_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

if not os.listdir(TEMPLATES_DIR):
    os.makedirs(os.path.join(TEMPLATES_DIR, "Blu-ray"), exist_ok=True)
