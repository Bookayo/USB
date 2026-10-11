"""Tests the real ElevenLabs calls one at a time. Uses credits (a little).

Usage:   python test_elevenlabs.py path\to\recording.m4a
(Mac:    python3 test_elevenlabs.py path/to/recording.m4a)

Safe to delete once everything passes.
"""
import os
import sys

os.environ["USE_FAKES"] = "0"  # force the real API for this test

from services import elevenlabs_api as el  # noqa: E402

audio = sys.argv[1] if len(sys.argv) > 1 else "test.wav"
if not os.path.exists(audio):
    sys.exit(f"Recording not found: {audio}\nPass the path as an argument.")

results = {}
voice_id = None


def run(name, fn):
    try:
        out = fn()
        print(f"PASS  {name}: {out}")
        results[name] = True
        return out
    except Exception as e:
        print(f"FAIL  {name}: {type(e).__name__}: {e}")
        results[name] = False
        return None


print("1/4 transcribe")
run("transcribe", lambda: el.transcribe(audio))

print("2/4 clone_voice")
voice_id = run("clone_voice", lambda: el.clone_voice(audio))

print("3/4 speak (needs the clone)")
if voice_id:
    run("speak", lambda: el.speak("Hello, this is my cloned voice singing about oat milk.", voice_id))
else:
    print("SKIP  speak (clone_voice failed)")

print("4/4 make_backing_track")
run("make_backing_track", lambda: el.make_backing_track("upbeat funk"))

if voice_id:
    print("cleanup: deleting the test voice")
    run("delete_voice", lambda: el.delete_voice(voice_id))

print()
print("Summary:", ", ".join(f"{k}={'ok' if v else 'FAILED'}" for k, v in results.items()))
print("Listen to the files in outputs/ to check they sound right.")
