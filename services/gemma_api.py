"""Gemma 4 wrapper (Person B). Keep the function signature stable.

TODO for Person B: set MODEL to the Gemma 4 model name shown in the Gemini API
docs / Google AI Studio, then implement the real branch with the `google-genai`
package. Most of the humour comes from the prompt, so spend time on it.
"""
import os

from dotenv import load_dotenv

load_dotenv()

MODEL = "TODO-gemma-4-model-name"

SYSTEM_PROMPT = (
    "You write ridiculous, funny song lyrics from a spoken prompt. "
    "Return a title, 8-16 lines of lyrics, and a one-line music style description "
    "(genre, tempo, mood) suitable for a music generator."
)


def _fakes() -> bool:
    return os.getenv("USE_FAKES", "1") == "1"


def make_lyrics(transcript: str) -> dict:
    """Returns {"lyrics": str, "style": str, "title": str}."""
    if _fakes():
        return {
            "title": "Oat Milk Betrayal",
            "style": "slow dramatic power ballad, piano and strings",
            "lyrics": f"Oh, {transcript}...\nThe fridge is empty now.\nThe fridge is empty now.",
        }
    # TODO: from google import genai; client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    # then client.models.generate_content(model=MODEL, contents=...) and parse the result
    # into the dict above (asking for JSON output makes parsing easy).
    raise NotImplementedError("make_lyrics: implement with the Gemma 4 / Gemini API")
