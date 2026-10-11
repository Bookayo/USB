import json
import os
import re
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Gemma 4 instruction-tuned model on Gemini API / Google AI Studio
MODEL = "gemma-4-26b-a4b-it"

SYSTEM_PROMPT = (
    "You write ridiculous, funny song lyrics from a spoken prompt. "
    "Return a title, 8-16 lines of lyrics, and a one-line music style description "
    "(genre, tempo, mood) suitable for a music generator. "
    "Respond ONLY with a raw JSON object (no markdown fences, no explanatory text) matching this format:\n"
    "{\n"
    '  "title": "Song Title",\n'
    '  "style": "genre, tempo, instrumentation, mood",\n'
    '  "lyrics": "[Verse 1]\\n...\\n[Chorus]\\n...\\n[Fade Out]\\n..."\n'
    "}"
)


def _fakes() -> bool:
    return os.getenv("USE_FAKES", "1") == "1"


def make_lyrics(transcript: str, vibe: str = "Ridiculous & Melodramatic") -> dict:
    """Returns {"lyrics": str, "style": str, "title": str}."""
    if _fakes():
        return {
            "title": "Oat Milk Betrayal",
            "style": f"slow dramatic power ballad, piano and strings, {vibe.lower()} mood",
            "lyrics": f"Oh, {transcript}...\nThe fridge is empty now.\nThe fridge is empty now."
        }

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in your .env file.")

    client = genai.Client(api_key=api_key)

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Desired Mood/Humor Level: {vibe}\n"
        f"Transform this spoken transcript into a song matching that mood:\n"
        f'"{transcript}"'
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    text = response.text.strip()

    # Extract JSON object even if the model surrounds it with backticks
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        data = json.loads(match.group(0))
    else:
        data = json.loads(text)

    return {
        "title": data.get("title", "Untitled Song"),
        "style": data.get("style", "upbeat pop, acoustic guitar, cheerful"),
        "lyrics": data.get("lyrics", text),
    }