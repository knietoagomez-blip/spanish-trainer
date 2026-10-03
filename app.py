"""
app.py — the web server (Flask).

Flask is a small Python library that creates a local web server.
When you run this file, it starts listening at http://localhost:5000.
Your browser talks to it just like it would talk to any website,
except everything stays on your own computer.
"""

import os
import tempfile

from flask import Flask, render_template, jsonify, request
from database import init_db, get_all_cards, add_card, add_cards_bulk
from whisper_module import transcribe_audio_file
from analysis_seam import parse_cards_from_text

app = Flask(__name__)

# Create the database tables the first time the app runs.
# On every restart after that, init_db() just checks they exist (safe to call repeatedly).
init_db()


# ── Page routes (serve the HTML) ──────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


# ── API routes (serve data as JSON for the JavaScript to use) ─────────────────
# JSON is a simple text format for sending structured data between Python and JS.

@app.route('/api/cards')
def list_cards():
    """Return all saved cards and a count."""
    cards = get_all_cards()
    return jsonify({'cards': cards, 'count': len(cards)})


@app.route('/api/add-test-card', methods=['POST'])
def add_test_card():
    """
    Phase 1 test endpoint — adds a dummy card so you can verify
    that data survives an app restart. Safe to call multiple times.
    """
    add_card(
        prompt='I went to the supermarket yesterday (Phase 1 storage test)',
        spanish='Fui al supermercado ayer',
        error_type='preterite_vs_imperfect',
    )
    cards = get_all_cards()
    return jsonify({
        'message': 'Test card saved to the database!',
        'total_cards': len(cards),
    })


@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    """
    Receive an audio recording from the browser, run Whisper on it,
    and return the Spanish transcript as text.

    The browser sends the audio as a "file upload" (like attaching a file
    to an email). Flask saves it to a temporary file, Whisper reads that
    file, then we delete the temp file.
    """
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file was received.'}), 400

    audio_file = request.files['audio']

    # Work out the file extension (.webm, .ogg, .mp4) from the MIME type.
    # MIME type is a label like "audio/webm" that tells software what kind of file it is.
    mime = audio_file.content_type or 'audio/webm'
    ext = '.' + mime.split('/')[1].split(';')[0]   # "audio/webm;codecs=opus" → ".webm"

    # Save the audio to a temporary file so Whisper can read it from disk.
    # delete=False means we control when to delete it (we do it in the finally block).
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        audio_file.save(tmp.name)
        tmp_path = tmp.name

    try:
        text = transcribe_audio_file(tmp_path)
        return jsonify({'transcript': text})
    except Exception as e:
        return jsonify({'error': 'Transcription failed: ' + str(e)}), 500
    finally:
        os.unlink(tmp_path)   # always delete the temp file, even if something went wrong


@app.route('/api/parse-cards', methods=['POST'])
def parse_cards():
    """
    ── ANALYSIS SEAM ENTRY POINT ──
    Receive pasted card text from the browser, run it through the
    analysis_seam parser, and return the parsed cards for preview.
    Nothing is saved yet — the user confirms first.
    """
    data = request.get_json()
    raw_text = data.get('text', '')

    if not raw_text.strip():
        return jsonify({'error': 'Please paste some card text first.'}), 400

    cards, errors = parse_cards_from_text(raw_text)
    return jsonify({'cards': cards, 'errors': errors, 'count': len(cards)})


@app.route('/api/save-cards', methods=['POST'])
def save_cards():
    """Save a confirmed list of cards to the database."""
    data = request.get_json()
    cards = data.get('cards', [])

    if not cards:
        return jsonify({'error': 'No cards to save.'}), 400

    add_cards_bulk(cards)
    return jsonify({'message': f'{len(cards)} card(s) saved!', 'count': len(cards)})


# ── Start the server ──────────────────────────────────────────────────────────

if __name__ == '__main__':
    print()
    print('  Spanish Trainer v0.5 is running!')
    print('  Open your browser to:  http://localhost:5001')
    print('  Press Ctrl+C to stop.')
    print()
    # debug=True means the server restarts automatically when you edit a file.
    # It also shows detailed error messages in the browser.
    app.run(debug=True, port=5001)
