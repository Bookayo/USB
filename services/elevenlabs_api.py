"""ElevenLabs wrapper. Keep these function signatures stable.

With USE_FAKES=1 (the default in .env.example) everything returns fake data,
so the rest of the team can build without API keys or credits.

With USE_FAKES=0 the real ElevenLabs API is used. Status of the real calls:
  transcribe          tested, works
  make_backing_track  tested, works
  clone_voice         fixed (labels must be a plain dict), retest
  speak               not tested yet (needs clone_voice)
If a call fails, check the installed SDK (`pip show elevenlabs`) and the docs:
https://elevenlabs.io/docs/api-reference
"""
import os
import uuid

from dotenv import load_dotenv

from audio_utils import make_test_tone

load_dotenv()

STT_MODEL = "scribe_v2"
BACKING_LENGTH_MS = 30000  # 30s keeps credits and waiting time down; docs allow 3000-600000


def _fakes() -> bool:
    return os.getenv("USE_FAKES", "1") == "1"


def _denoise() -> bool:
    """CLONE_DENOISE=1 in .env cleans background noise from the voice sample.

    Use it for noisy recordings (e.g. a busy hall). The docs warn it can make
    quality WORSE on audio that is already clean, so it is off by default.
    """
    return os.getenv("CLONE_DENOISE", "0") == "1"


def _client():
    from elevenlabs.client import ElevenLabs

    key = os.getenv("ELEVENLABS_API_KEY")
    if not key:
        raise RuntimeError("ELEVENLABS_API_KEY is not set in .env")
    return ElevenLabs(api_key=key)


def _out(prefix: str) -> str:
    os.makedirs("outputs", exist_ok=True)
    return os.path.join("outputs", f"{prefix}_{uuid.uuid4().hex[:8]}.mp3")


def _save_audio(audio, path: str) -> str:
    """The SDK returns audio as bytes or an iterator of byte chunks. Handle both."""
    with open(path, "wb") as f:
        if isinstance(audio, (bytes, bytearray)):
            f.write(audio)
        else:
            for chunk in audio:
                if chunk:
                    f.write(chunk)
    return path


def transcribe(audio_path: str) -> str:
    """Speech to text. Returns what the user said."""
    if _fakes():
        return "a power ballad about my flatmate stealing my oat milk"
    with open(audio_path, "rb") as f:
        result = _client().speech_to_text.convert(file=f, model_id=STT_MODEL)
    return result.text


def clone_voice(audio_path: str) -> str:
    """Instant voice clone from the user's recording. Returns a voice_id.

    Needs a plan that includes instant voice cloning.
    Set CLONE_DENOISE=1 in .env to remove background noise from the sample.
    """
    if _fakes():
        return "fake-voice-id"
    with open(audio_path, "rb") as f:
        voice = _client().voices.ivc.create(
            name=f"song-{uuid.uuid4().hex[:6]}",
            files=[f],
            remove_background_noise=_denoise(),
            # The SDK runs json.dumps() on labels itself and sends a bad value if
            # labels is omitted, so pass a plain dict (NOT a JSON string).
            labels={"source": "hackathon"},
        )
    return voice.voice_id


def speak(text: str, voice_id: str) -> str:
    """Text to speech in the cloned voice. Returns an audio file path."""
    if _fakes():
        return make_test_tone(_out("fake_speech"), seconds=6, freq=660)
    audio = _client().text_to_speech.convert(voice_id=voice_id, text=text)
    return _save_audio(audio, _out("speech"))


def make_backing_track(style: str) -> str:
    """Generate an instrumental backing track for the given style. Returns an audio file path."""
    if _fakes():
        return make_test_tone(_out("fake_backing"), seconds=3, freq=220)
    audio = _client().music.compose(
        prompt=f"{style}. Instrumental backing track, no vocals.",
        music_length_ms=BACKING_LENGTH_MS,
        force_instrumental=True,
    )
    return _save_audio(audio, _out("backing"))


def delete_voice(voice_id: str) -> None:
    """Optional cleanup: each clone uses a voice slot. Not part of the contract.

    Person C can call this from pipeline.py after the song is made if slots run out.
    """
    if _fakes() or voice_id == "fake-voice-id":
        return
    _client().voices.delete(voice_id=voice_id)
