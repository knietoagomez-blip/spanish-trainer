"""
whisper_module.py — local speech-to-text using OpenAI Whisper.

"Speech-to-text" means converting spoken audio into written words.
Whisper is an open-source model made by OpenAI. Unlike their paid API,
this version runs entirely on your Mac — no internet, no API key, free.

The model file (~74 MB, called "base") is downloaded automatically the
first time you transcribe something, then saved to your Mac and reused
every time after. You'll see a progress bar in the terminal.
"""

import whisper
import os

# This holds the loaded model in memory between requests.
# We use None as a placeholder meaning "not loaded yet".
_model = None


def get_model():
    """
    Load Whisper into memory. First call downloads the model (~74 MB).
    Every call after that is instant — it's already in memory.
    """
    global _model
    if _model is None:
        print("  Loading Whisper 'base' model...")
        print("  (First time: downloads ~74 MB — you will see a progress bar.)")
        _model = whisper.load_model("base")
        print("  Whisper model ready.")
    return _model


def transcribe_audio_file(file_path):
    """
    Transcribe a Spanish audio file to text.

    file_path — path to the audio file saved on disk
    Returns   — the transcribed text as a plain string
    """
    model = get_model()

    # language="es" means Spanish ("es" is the standard code for español).
    # Telling Whisper the language makes it faster and more accurate than
    # letting it guess.
    result = model.transcribe(file_path, language="es")
    return result["text"].strip()
