# Spanish Trainer

A local, voice-enabled Spanish practice app built for heritage speakers who understand far more than they can comfortably say.

## How it works

1. **Speak.** Record yourself talking in Spanish. Audio is transcribed on your own machine with OpenAI's open-source Whisper model.
2. **Analyze.** The transcript is reviewed by an AI model for grammar, word choice, and phrasing mistakes, which come back as flashcards.
3. **Review.** Cards are stored in a local SQLite database and scheduled with spaced repetition, with a review log and daily streak.

## Design choice: a clean analysis seam

All card generation lives in `analysis_seam.py`, behind a fixed input/output contract. Version 0.5 uses a free manual step (paste the transcript into an AI chat, paste the cards back). A later version can swap in a direct API call without touching transcription, storage, or review code.

## Stack

Python, Flask, Whisper, SQLite, vanilla HTML/JS.

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000. Whisper also needs `ffmpeg` installed.
