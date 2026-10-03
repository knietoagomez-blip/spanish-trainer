"""
analysis_seam.py — THE ISOLATED ANALYSIS / CARD-GENERATION SEAM
================================================================

This module is the ONLY place where transcripts turn into flashcards.
It is deliberately kept separate from all other code.

CURRENT behavior (Phase 4 — manual):
  The user copies the session transcript, pastes it into an external
  AI chat, gets back a list of cards in the defined text format, and
  pastes that list into the "Import Cards" box in the app.
  This module parses that pasted text into card objects.

FUTURE behavior (automated upgrade):
  Replace `generate_cards_from_transcript()` below with a version
  that calls an LLM API directly. The rest of the app (transcription,
  storage, review, report) does NOT need to change at all.

CONTRACT — do not change these shapes:
  Input  to parse_cards_from_text():
      raw_text (str) — the multi-line pasted card list
  Output of parse_cards_from_text():
      (cards, errors)
        cards  — list of dicts, each with keys:
                   prompt     (str)  English prompt with context cue
                   spanish    (str)  correct Spanish answer
                   error_type (str)  one of VALID_ERROR_TYPES
        errors — list of human-readable strings describing bad lines

  Input  to generate_cards_from_transcript() [FUTURE SEAM POINT]:
      transcript (str) — raw session transcript text
  Output:
      list of card dicts (same shape as above)
================================================================
"""

# The only error types the rest of the app knows about
VALID_ERROR_TYPES = {
    'preterite_vs_imperfect',
    'ser_vs_estar',
    'subjunctive',
    'gender_agreement',
    'word_retrieval',
    'other',
}


def parse_cards_from_text(raw_text):
    """
    Parse a pasted block of card text into a list of card dicts.

    Expected format — one card per line:
        English prompt (context cue) | correct Spanish | error_type

    Blank lines are skipped. Bad lines are collected as error messages.
    Returns (list_of_valid_cards, list_of_error_strings).
    """
    cards = []
    errors = []

    for line_num, line in enumerate(raw_text.strip().splitlines(), start=1):
        line = line.strip()
        if not line:
            continue  # skip blank lines silently

        parts = line.split('|')
        if len(parts) != 3:
            errors.append(
                f'Line {line_num}: expected 3 parts separated by "|", got {len(parts)} — skipped.'
            )
            continue

        prompt, spanish, error_type = [p.strip() for p in parts]
        error_type = error_type.lower()

        if not prompt or not spanish:
            errors.append(f'Line {line_num}: prompt and Spanish answer cannot be empty — skipped.')
            continue

        if error_type not in VALID_ERROR_TYPES:
            errors.append(
                f'Line {line_num}: unknown error_type "{error_type}" — saved as "other".'
            )
            error_type = 'other'

        cards.append({
            'prompt': prompt,
            'spanish': spanish,
            'error_type': error_type,
        })

    return cards, errors


# ================================================================
# FUTURE SEAM POINT — replace this function body for API upgrade
# ================================================================
def generate_cards_from_transcript(transcript):
    """
    FUTURE: automatically generate cards from a transcript.

    Currently raises NotImplementedError — the manual copy-paste flow
    is used instead (see parse_cards_from_text above).

    When upgrading: implement this function to call an LLM API with
    `transcript` and return a list of card dicts. The app will call
    this instead of showing the manual import box.
    """
    raise NotImplementedError(
        'Automated card generation is not yet implemented. '
        'Use the manual Import Cards flow instead.'
    )
