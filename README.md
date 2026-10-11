# Say-nthesizer (working title)

Speak a prompt, get a song in your own voice.
ElevenLabs (transcribe, clone, speak, music) + Gemma 4 (lyrics) + Streamlit UI.

---

## Setup (copy and paste)

Open a terminal **inside the project folder**, then paste the blocks for your computer.
Requires Python 3.10 or newer.

### Windows (PowerShell)

Block 1. Paste all of it:
```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
winget install Gyan.FFmpeg
copy .env.example .env
```

Now **close the terminal and open a new one in the project folder** (needed so ffmpeg is found).

Block 2. Paste all of it:
```
.venv\Scripts\Activate.ps1
ffmpeg -version
streamlit run app.py
```

Using Command Prompt (cmd) instead of PowerShell? Replace `.venv\Scripts\Activate.ps1` with `.venv\Scripts\activate` in both blocks.

If PowerShell says scripts are disabled, run this once, then redo Block 1:
```
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### Mac (Terminal)

Paste all of it:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
brew install ffmpeg
cp .env.example .env
ffmpeg -version
streamlit run app.py
```

If `brew` is not found, install Homebrew first from https://brew.sh and run the block again.

### Every time after that

Windows (PowerShell):
```
.venv\Scripts\Activate.ps1
streamlit run app.py
```

Mac:
```
source .venv/bin/activate
streamlit run app.py
```

### Fill in your .env

Open the `.env` file in any text editor and add your keys:
- `ELEVENLABS_API_KEY` : from your ElevenLabs account settings
- `GEMINI_API_KEY` : from Google AI Studio
- `OPENLOFT_API_KEY` : only needed once the memory feature is built
- `USE_FAKES` : leave as `1` until the real API code works (fake data, no credits used). Set to `0` to use the real APIs.

Never share or upload `.env`.

---

## Troubleshooting

| Error | Fix |
|---|---|
| `No module named 'audioop'` or `'pyaudioop'` | You are on Python 3.13+. Run `pip install -r requirements.txt` again (it includes `audioop-lts`). |
| `ffmpeg` is not recognized / `command not found` | Close the terminal, open a new one, activate the venv again. If still missing, run the ffmpeg install line again. |
| `winget` is not recognized | Download ffmpeg from https://www.gyan.dev/ffmpeg/builds/ (release essentials zip), unzip to `C:\ffmpeg`, add `C:\ffmpeg\bin` to PATH. |
| `streamlit` is not recognized / `command not found` | The venv is not activated. Run the activate line. |
| `No module named 'dotenv'` (or another package) | Venv not activated, or run `pip install -r requirements.txt` again. |
| Keys not being picked up | The file must be named exactly `.env` (not `.env.txt`) and sit in the project root. |

---

## Who owns what

| Person | Files |
|---|---|
| A: Frontend / demo | `app.py`, `assets/`, CSS, visualiser, pitch |
| B: AI / APIs | `services/elevenlabs_api.py`, `services/gemma_api.py` |
| C: Audio / pipeline | `pipeline.py`, `audio_utils.py`, `services/memory.py`, `assets/fallback_song.mp3` |

Only edit your own files. If you need a change in someone else's file, message them.

## Function contract (do not change signatures without telling everyone)
```python
gemma_api.make_lyrics(transcript: str) -> dict      # {"lyrics", "style", "title"}
elevenlabs_api.transcribe(audio_path: str) -> str
elevenlabs_api.clone_voice(audio_path: str) -> str  # voice_id
elevenlabs_api.speak(text: str, voice_id: str) -> str          # audio file path
elevenlabs_api.make_backing_track(style: str) -> str           # audio file path
pipeline.make_song(audio_path: str) -> dict         # {"audio_path","title","lyrics","transcript"}
```
