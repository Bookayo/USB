"""Audio in -> song out (Person C). app.py only calls make_song()."""
import os
import time
import uuid

from dotenv import load_dotenv

from audio_utils import mix_voice_over_backing
from services import elevenlabs_api as eleven
from services import gemma_api as gemma
from services import memory

load_dotenv()

FALLBACK_SONG = os.path.join("assets", "fallback_song.mp3")  # drop an emergency song here


def _step(name, fn, *args):
    t = time.time()
    result = fn(*args)
    print(f"[pipeline] {name}: {time.time() - t:.1f}s")
    return result


def make_song(audio_path: str) -> dict:
    """Returns {"audio_path", "title", "lyrics", "transcript"}."""
    try:
        transcript = _step("transcribe", eleven.transcribe, audio_path)
        voice_id = _step("clone_voice", eleven.clone_voice, audio_path)
        song = _step("make_lyrics", gemma.make_lyrics, transcript)  # {"lyrics","style","title"}
        speech = _step("speak", eleven.speak, song["lyrics"], voice_id)
        backing = _step("backing_track", eleven.make_backing_track, song["style"])

        out_path = os.path.join("outputs", f"song_{uuid.uuid4().hex[:8]}.mp3")
        final = _step("mix", mix_voice_over_backing, speech, backing, out_path)

        result = {
            "audio_path": final,
            "title": song["title"],
            "lyrics": song["lyrics"],
            "transcript": transcript,
        }
        try:
            memory.remember_song(result)  # optional discography feature
        except Exception as e:
            print(f"[pipeline] memory skipped: {e}")
        return result
    except Exception as e:
        # Never crash the demo: fall back to a pre-made song if one exists.
        print(f"[pipeline] FAILED: {e}")
        if os.path.exists(FALLBACK_SONG):
            return {
                "audio_path": FALLBACK_SONG,
                "title": "Technical Difficulties (The Musical)",
                "lyrics": "The API has left the building.",
                "transcript": "",
            }
        raise
