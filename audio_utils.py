"""Audio helpers (Person C). Needs ffmpeg installed: run `ffmpeg -version` to check."""
import os

from pydub import AudioSegment
from pydub.effects import normalize
from pydub.generators import Sine
from pydub.silence import detect_leading_silence


def make_test_tone(path: str, seconds: float = 3.0, freq: int = 440) -> str:
    """Write a simple tone to `path`. Used by the fake service stubs."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tone = Sine(freq).to_audio_segment(duration=int(seconds * 1000)).apply_gain(-12)
    tone.export(path, format="mp3")
    return path


def trim_leading_silence(seg: AudioSegment, threshold_db: int = -40) -> AudioSegment:
    start = detect_leading_silence(seg, silence_threshold=threshold_db)
    return seg[start:]


def mix_voice_over_backing(
    voice_path: str,
    backing_path: str,
    out_path: str,
    backing_gain_db: float = -8.0,
    tail_ms: int = 2000,
) -> str:
    """Overlay the voice on the backing track and export an mp3.

    - Backing track is looped/trimmed to fit the voice length plus a short tail.
    - Backing is turned down (backing_gain_db) so the voice stays on top.
    - Result is normalised so the volume is consistent between songs.
    """
    voice = trim_leading_silence(AudioSegment.from_file(voice_path))
    backing = AudioSegment.from_file(backing_path)

    target_len = len(voice) + tail_ms
    if len(backing) < target_len:
        loops = target_len // max(len(backing), 1) + 1
        backing = backing * loops
    backing = backing[:target_len].fade_out(1500).apply_gain(backing_gain_db)

    mixed = normalize(backing.overlay(voice, position=0))

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    mixed.export(out_path, format="mp3")
    return out_path


if __name__ == "__main__":
    # Quick self-test with generated tones, no APIs needed:  python audio_utils.py
    v = make_test_tone("outputs/_test_voice.mp3", 4, 880)
    b = make_test_tone("outputs/_test_backing.mp3", 2, 220)
    print("Wrote", mix_voice_over_backing(v, b, "outputs/_test_mix.mp3"))
