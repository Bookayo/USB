# Say-nthesizer (working title)

Speak a prompt, get a song in your own voice. ElevenLabs (transcribe, clone, speak, music) + Gemma 4 (lyrics) + Streamlit UI.

## Setup
1. Install Python 3.10+ and **ffmpeg** (check with `ffmpeg -version`).
2. `python -m venv .venv` then activate it (`.venv\Scripts\activate` on Windows).
3. `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your keys (never commit `.env`).
5. `streamlit run app.py`

`USE_FAKES=1` in `.env` makes the services return fake audio so you can build without spending credits.

## Who owns what
| Person | Files |
|---|---|
| A: Frontend / demo | `app.py`, `assets/`, CSS, visualiser, pitch |
| B: AI / APIs | `services/elevenlabs_api.py`, `services/gemma_api.py` |
| C: Audio / pipeline | `pipeline.py`, `audio_utils.py`, `services/memory.py`, repo setup |

## Function contract (don't change signatures without telling everyone)
```python
gemma_api.make_lyrics(transcript: str) -> dict      # {"lyrics", "style", "title"}
elevenlabs_api.transcribe(audio_path: str) -> str
elevenlabs_api.clone_voice(audio_path: str) -> str  # voice_id
elevenlabs_api.speak(text: str, voice_id: str) -> str          # audio file path
elevenlabs_api.make_backing_track(style: str) -> str           # audio file path
pipeline.make_song(audio_path: str) -> dict         # {"audio_path","title","lyrics","transcript"}
```

## Rules
- Pull from `main` before starting, commit small and often.
- Only clone voices of people who have agreed to it.
- Keep a fallback song in `assets/fallback_song.mp3` for the demo.
