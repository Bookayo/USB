"""ElevenLabs wrapper (Person B). Keep these function signatures stable.

With USE_FAKES=1 (the default in .env.example) everything returns fake data,
so the rest of the team can build without API keys or credits.

TODO for Person B: replace each real branch using the official `elevenlabs`
Python SDK. Check the current docs for the exact calls, especially for
music generation and whether cloned voices can sing:
https://elevenlabs.io/docs
"""
import os
import uuid

from dotenv import load_dotenv

from audio_utils import make_test_tone

load_dotenv()


def _fakes() -> bool:
    return os.getenv("USE_FAKES", "1") == "1"


def _client():
    from elevenlabs.client import ElevenLabs

    return ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))


def _out(prefix: str) -> str:
    return os.path.join("outputs", f"{prefix}_{uuid.uuid4().hex[:8]}.mp3")


def transcribe(audio_path: str) -> str:
    """Speech to text. Returns what the user said."""
    if _fakes():
        return "a power ballad about my flatmate stealing my oat milk"
    # TODO: use the speech-to-text endpoint via _client()
    raise NotImplementedError("transcribe: implement with the ElevenLabs STT API")


def clone_voice(audio_path: str) -> str:
    """Instant voice clone from the user's recording. Returns a voice_id."""
    if _fakes():
        return "fake-voice-id"
    # TODO: use the instant voice cloning endpoint via _client()
    raise NotImplementedError("clone_voice: implement with the ElevenLabs voice cloning API")


def speak(text: str, voice_id: str) -> str:
    """Text to speech in the cloned voice. Returns an audio file path."""
    if _fakes():
        return make_test_tone(_out("fake_speech"), seconds=6, freq=660)
    # TODO: use text-to-speech with voice_id via _client(), write bytes to _out("speech")
    raise NotImplementedError("speak: implement with the ElevenLabs TTS API")


def make_backing_track(style: str) -> str:
    """Generate a backing track for the given style description. Returns an audio file path."""
    if _fakes():
        return make_test_tone(_out("fake_backing"), seconds=3, freq=220)
    # TODO: use the ElevenLabs music generation API (check docs for availability)
    raise NotImplementedError("make_backing_track: implement with the ElevenLabs music API")
