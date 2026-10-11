"""Say-nthesizer: Streamlit UI.  Run with:  streamlit run app.py

Needs Streamlit >= 1.40. Keep this file next to pipeline.py, and the theme in
.streamlit/config.toml.
"""
import html
import mimetypes
import os
import re
import shutil
import tempfile
import urllib.parse
import warnings

import streamlit as st


def _ensure_ffmpeg() -> None:
    """If ffmpeg isn't on PATH, fall back to the copy bundled with imageio-ffmpeg."""
    if shutil.which("ffmpeg"):
        return
    try:
        import imageio_ffmpeg
    except ImportError:
        return  # install ffmpeg properly, or `pip install imageio-ffmpeg`
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        from pydub import AudioSegment
    AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()


_ensure_ffmpeg()

from pipeline import make_song  # noqa: E402  (must come after the ffmpeg check)

st.set_page_config(page_title="Say-nthesizer", page_icon="🎤", layout="wide")

SWATCHES = ["#A879FF", "#62D6C5", "#D5B8FF", "#7B4BB7"]

EXAMPLES = [
    "A power ballad about my flatmate stealing my oat milk",
    "A sea shanty about a late train",
    "A lullaby for a very anxious cat",
]

# Gig-poster wallpaper tile: vinyl, notes, a mic, equaliser bars, a soundwave, sparkles.
PATTERN_SVG = """<svg xmlns='http://www.w3.org/2000/svg' width='560' height='560' viewBox='0 0 560 560'>
<g transform='translate(110 120)'>
<circle r='64' fill='#173F3C' fill-opacity='.7'/>
<circle r='52' fill='none' stroke='#F6E8C3' stroke-opacity='.12' stroke-width='1.5'/>
<circle r='42' fill='none' stroke='#F6E8C3' stroke-opacity='.12' stroke-width='1.5'/>
<circle r='32' fill='none' stroke='#F6E8C3' stroke-opacity='.12' stroke-width='1.5'/>
<circle r='20' fill='#F2B632' fill-opacity='.9'/>
<circle r='3.5' fill='#173F3C'/>
<path d='M-50 -34 A60 60 0 0 1 -30 -53' stroke='#F6E8C3' stroke-opacity='.4' stroke-width='4' fill='none' stroke-linecap='round'/>
</g>
<g transform='translate(432 402) rotate(20)'>
<circle r='48' fill='#173F3C' fill-opacity='.7'/>
<circle r='38' fill='none' stroke='#F6E8C3' stroke-opacity='.12' stroke-width='1.5'/>
<circle r='29' fill='none' stroke='#F6E8C3' stroke-opacity='.12' stroke-width='1.5'/>
<circle r='16' fill='#E8662A' fill-opacity='.9'/>
<circle r='3' fill='#173F3C'/>
<path d='M-38 -24 A45 45 0 0 1 -22 -39' stroke='#F6E8C3' stroke-opacity='.4' stroke-width='3.5' fill='none' stroke-linecap='round'/>
</g>
<g transform='translate(330 66) rotate(-8)' fill='#7FB8AE' fill-opacity='.55'>
<ellipse cx='0' cy='38' rx='13' ry='9' transform='rotate(-20 0 38)'/>
<rect x='10' y='-8' width='4' height='46'/>
<path d='M14 -8 C32 0 38 16 30 32 C36 14 26 8 14 8 Z'/>
</g>
<g transform='translate(58 376) rotate(6)' fill='#F6E8C3' fill-opacity='.4'>
<ellipse cx='0' cy='40' rx='13' ry='9' transform='rotate(-20 0 40)'/>
<ellipse cx='34' cy='34' rx='13' ry='9' transform='rotate(-20 34 34)'/>
<rect x='10' y='-6' width='4' height='46'/>
<rect x='44' y='-14' width='4' height='44'/>
<polygon points='10,-6 48,-14 48,-2 10,6'/>
</g>
<g transform='translate(190 322)'>
<rect x='-14' y='-30' width='28' height='44' rx='14' fill='#E8662A' fill-opacity='.7'/>
<path d='M-14 -16 H14 M-14 -6 H14 M-14 4 H14' stroke='#173F3C' stroke-opacity='.5' stroke-width='2'/>
<path d='M-24 2 A24 24 0 0 0 24 2' fill='none' stroke='#F6E8C3' stroke-opacity='.5' stroke-width='3' stroke-linecap='round'/>
<path d='M0 26 V40 M-12 40 H12' stroke='#F6E8C3' stroke-opacity='.5' stroke-width='3' stroke-linecap='round'/>
</g>
<g transform='translate(262 480)' stroke='#173F3C' stroke-opacity='.45' stroke-width='2'>
<rect x='0' y='-40' width='13' height='40' fill='#F2B632' fill-opacity='.75'/>
<rect x='20' y='-80' width='13' height='80' fill='#7FB8AE' fill-opacity='.5'/>
<rect x='40' y='-55' width='13' height='55' fill='#E8662A' fill-opacity='.7'/>
<rect x='60' y='-100' width='13' height='100' fill='#F6E8C3' fill-opacity='.4'/>
<rect x='80' y='-30' width='13' height='30' fill='#7FB8AE' fill-opacity='.5'/>
<rect x='100' y='-70' width='13' height='70' fill='#F2B632' fill-opacity='.75'/>
</g>
<path d='M0 262 Q35 214 70 262 T140 262 T210 262 T280 262 T350 262 T420 262 T490 262 T560 262' fill='none' stroke='#F6E8C3' stroke-opacity='.2' stroke-width='3'/>
<g fill='#F6E8C3' fill-opacity='.6'>
<path transform='translate(236 186)' d='M0 -14 Q2 -2 14 0 Q2 2 0 14 Q-2 2 -14 0 Q-2 -2 0 -14Z'/>
<path transform='translate(500 150) scale(.8)' d='M0 -14 Q2 -2 14 0 Q2 2 0 14 Q-2 2 -14 0 Q-2 -2 0 -14Z'/>
<path transform='translate(36 238) scale(.7)' d='M0 -14 Q2 -2 14 0 Q2 2 0 14 Q-2 2 -14 0 Q-2 -2 0 -14Z'/>
<path transform='translate(520 330) scale(.9)' d='M0 -14 Q2 -2 14 0 Q2 2 0 14 Q-2 2 -14 0 Q-2 -2 0 -14Z'/>
<path transform='translate(410 262) scale(.6)' d='M0 -14 Q2 -2 14 0 Q2 2 0 14 Q-2 2 -14 0 Q-2 -2 0 -14Z'/>
</g>
<g fill-opacity='.7'>
<circle cx='160' cy='40' r='5' fill='#F2B632'/>
<circle cx='470' cy='230' r='6' fill='#E8662A'/>
<circle cx='400' cy='520' r='5' fill='#7FB8AE'/>
<circle cx='30' cy='500' r='6' fill='#F2B632'/>
<circle cx='520' cy='60' r='5' fill='#E8662A'/>
</g>
</svg>"""

PATTERN_URI = "data:image/svg+xml;utf8," + urllib.parse.quote(PATTERN_SVG)

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Figtree:wght@400;500;600&display=swap');

:root {
  --card: #282238;
  --cream: #F0EAF8;
  --ink: #110D1A;
  --muted: #B4A9C9;
  --orange: #A879FF;
  --teal: #62D6C5;
  --yellow: #D5B8FF;
  --brick: #7B4BB7;
  --display: 'Bricolage Grotesque', 'Segoe UI', system-ui, sans-serif;
}

/* ---------- wallpaper: dusty teal, tone-on-tone doodles, 70s arcs ---------- */
.stApp {
  background-color: #171421;
  background-image:
    linear-gradient(135deg, #171421 0%, #21182F 55%, #171421 100%),
    url("__PATTERN__");
  background-size: 100% 100%, 100% 100%, 100% 100%, 560px 560px;
  background-repeat: no-repeat, repeat;
  background-attachment: fixed;
  color: var(--cream);
  font-family: 'Figtree', system-ui, sans-serif;
  color-scheme: dark;
}
[data-testid="stAppViewContainer"], [data-testid="stMain"] { background: transparent; }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"], footer, #MainMenu { visibility: hidden; }
.block-container { max-width: 1480px; padding: 2.4rem 2rem 1.5rem; }

/* ---------- hero ---------- */
.hero { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 0.8rem 1.5rem; margin-bottom: 1.4rem; }
.brand { display: flex; align-items: center; gap: 1rem; }
.pads { display: grid; grid-template-columns: repeat(4, 20px); gap: 5px; }
.pads i { display: block; height: 20px; border: 2px solid var(--ink); border-radius: 7px; }
.stApp .hero h1 {
  font-family: var(--display);
  font-weight: 800;
  font-size: clamp(2rem, 5vw, 3.3rem);
  letter-spacing: -0.035em;
  line-height: 1;
  margin: 0; padding: 0;
  color: var(--cream);
  text-shadow: 3px 3px 0 var(--ink);
}
.tagline {
  color: #171421;
  margin: 0;
  background: #D5B8FF;
  border: 2px solid var(--ink);
  border-radius: 999px;
  padding: 0.45rem 1.15rem;
  box-shadow: 3px 3px 0 var(--ink);
  font-family: var(--display);
  font-weight: 600;
  font-size: clamp(0.7rem, 2.9vw, 1.15rem);
  white-space: nowrap;
}

/* ---------- recorder panel ---------- */
.st-key-recorder {
  background: var(--card);
  border: 2px solid var(--ink);
  border-radius: 26px;
  padding: 1.4rem;
  box-shadow: 6px 6px 0 var(--ink);
}
.panel-title { font-family: var(--display); font-weight: 800; font-size: 1.4rem; letter-spacing: -0.01em; }
.panel-sub { color: var(--muted); margin: 0.15rem 0 0.9rem; }
[data-testid="stAudioInput"] > div {
  border: 2px solid #A879FF !important;
  border-radius: 16px !important;
  background: #302641 !important;
  color: #F0EAF8 !important;
}

[data-testid="stAudioInput"] button {
  background: #302641 !important;
  color: #F0EAF8 !important;
  border-color: #A879FF !important;
}
.hint { color: var(--muted); font-size: 0.9rem; margin: 0.9rem 0 0.4rem; }
.chips { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.1rem; }
.chip {
  border: 1.5px solid #71549B;
  border-radius: 999px;
  padding: 0.25rem 0.8rem;
  font-size: 0.88rem;
  background: #302641;
  color: #F0EAF8;
}
/* ---------- buttons ---------- */
.stApp .stButton, .stApp .stDownloadButton { width: 100%; }
.stApp .stButton > button,
.stApp .stDownloadButton > button {
  width: 100%;
  background: #302641;
  color: #F0EAF8;
  border: 2px solid #A879FF;
  border-radius: 999px;
  padding: 0.7rem 1.4rem;
  box-shadow: 3px 3px 0 #0D0914;
  transition: transform 0.08s ease, box-shadow 0.08s ease;
}
.stApp .stButton > button p,
.stApp .stDownloadButton > button p { font-family: var(--display); font-weight: 800; font-size: 1.1rem; color: inherit; }
.stApp .stDownloadButton > button { padding: 0.5rem 1rem; }
.stApp .stDownloadButton > button p { font-size: 0.95rem; }
.stApp .stButton > button[kind="primary"],
.stApp .stButton > button[data-testid="stBaseButton-primary"] { background: #A879FF; color: #171421; }
.stApp .stButton > button:hover,
.stApp .stDownloadButton > button:hover { transform: translate(-1px, -1px); box-shadow: 4px 4px 0 #0D0914; color: #171421; border-color: #C2A1FF; background: #C2A1FF;}
.stApp .stButton > button:active,
.stApp .stDownloadButton > button:active { transform: translate(3px, 3px); box-shadow: 0 0 0 var(--ink); }
.stApp .stButton > button:focus-visible,
.stApp .stDownloadButton > button:focus-visible { outline: 3px solid #62D6C5; outline-offset: 3px; }
.stApp .stButton > button:disabled,
.stApp .stButton > button[kind="primary"]:disabled,
.stApp .stButton > button[data-testid="stBaseButton-primary"]:disabled {
  background: #5B3D80 !important;
  color: #F0EAF8 !important;
  border: 2px solid #A879FF !important;
  box-shadow: none;
  transform: none;
  opacity: 1 !important;
  cursor: not-allowed;
}
.stApp .stButton > button:disabled p {
  color: #F0EAF8 !important;
  opacity: 1 !important;
}

/* ---------- generating animation ---------- */
.eq { display: flex; align-items: flex-end; gap: 6px; height: 56px; margin: 0.4rem 0; }
.eq span { width: 11px; height: 100%; border: 2px solid var(--ink); border-radius: 6px; animation: eq 0.9s ease-in-out infinite alternate; }
.eq span:nth-child(1) { background: var(--orange); animation-delay: -0.1s; }
.eq span:nth-child(2) { background: var(--teal);   animation-delay: -0.5s; }
.eq span:nth-child(3) { background: var(--yellow); animation-delay: -0.3s; }
.eq span:nth-child(4) { background: var(--brick);  animation-delay: -0.7s; }
.eq span:nth-child(5) { background: var(--orange); animation-delay: -0.2s; }
.eq span:nth-child(6) { background: var(--teal);   animation-delay: -0.6s; }
.eq span:nth-child(7) { background: var(--yellow); animation-delay: -0.4s; }
@keyframes eq { from { height: 14%; } to { height: 100%; } }
@media (prefers-reduced-motion: reduce) { .eq span { animation: none; height: 60%; } }
.eq-label { font-weight: 600; margin: 0 0 1rem; }

/* ---------- discography ---------- */
.section { display: flex; align-items: center; gap: 0.75rem; margin: 0.2rem 0 1rem; }
.stApp .section h2 {
  font-family: var(--display); font-weight: 800; font-size: 1.8rem; letter-spacing: -0.02em;
  margin: 0; padding: 0; color: var(--cream); text-shadow: 2px 2px 0 var(--ink);
}
.count { background: var(--yellow); border: 2px solid var(--ink); border-radius: 999px; padding: 0 0.65rem; font-weight: 600; font-size: 0.9rem; line-height: 1.5rem; }
.empty {
  box-sizing: border-box;
  width: 100%;
  border: 2px dashed #A879FF;
  border-radius: 20px;
  padding: 1.6rem 1.4rem;
  margin: 2px 0 6px;
  background: #282238 !important;
  color: #F0EAF8 !important;
  line-height: 1.7;
  overflow-wrap: anywhere;
}
.st-key-discography {
  max-height: calc(100vh - 12.5rem);
  overflow-y: auto;
  overflow-x: hidden;
  padding: 4px 12px 12px 4px;
  box-sizing: border-box;
}
@media (max-width: 900px) { .st-key-discography { max-height: none; overflow: visible; } }

[class*="st-key-song_"] {
  background: var(--card);
  border: 2px solid var(--ink);
  border-radius: 18px;
  padding: 1rem 1.2rem 1.15rem;
  box-shadow: 4px 4px 0 var(--ink);
}
.song-head { display: flex; align-items: center; gap: 0.9rem; }
.swatch { flex: none; width: 40px; height: 40px; border: 2px solid var(--ink); border-radius: 12px; }
.song-meta { color: var(--muted); font-size: 0.85rem; }
.song-title { font-family: var(--display); font-weight: 800; font-size: 1.3rem; letter-spacing: -0.015em; line-height: 1.15; }
[class*="st-key-song_"] audio { width: 100%; }
[class*="st-key-song_"] [data-testid="stExpander"] details {
  border: 2px solid #71549B;
  border-radius: 12px;
  background: #21182F !important;
  color: #F0EAF8;
}

[class*="st-key-song_"] [data-testid="stExpander"] summary {
  background: #21182F !important;
  color: #F0EAF8 !important;
}

[class*="st-key-song_"] .lyrics {
  color: #F0EAF8 !important;
}
[class*="st-key-song_"] [data-testid="stExpander"] summary { font-weight: 600; }
.lyrics { line-height: 1.7; max-width: 62ch; max-height: 240px; overflow-y: auto; padding: 0.25rem 0 0.5rem; }

[data-testid="stAlert"] { border: 2px solid var(--ink); border-radius: 14px; }

@media (max-width: 640px) { .block-container { padding: 2.2rem 1rem 1rem; } }
""".replace("__PATTERN__", PATTERN_URI)

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# Streamlit reruns the whole script on every interaction, so keep state here.
st.session_state.setdefault("songs", [])  # discography for this session
st.session_state.setdefault("rec_n", 0)  # bump to reset the recorder widget

if title := st.session_state.pop("just_made", None):
    st.toast(f"“{title}” is ready", icon="🎶")


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "song"


def generate(audio_file, vibe: str, slot) -> bool:
    """Run the pipeline on a recording, with an animation in `slot` while it works."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_file.getvalue())
        tmp_path = f.name

    slot.markdown(
        '<div class="eq" role="status" aria-label="Making your song">'
        + "<span></span>" * 7
        + '</div><p class="eq-label">Booking the studio… keep this tab open.</p>',
        unsafe_allow_html=True,
    )
    try:
        song = make_song(tmp_path, vibe=vibe)
    except Exception as e:  # noqa: BLE001 - surface any pipeline failure to the user
        slot.empty()
        st.error(f"Couldn't make that song: {e}. Your recording is still here, so you can try again.")
        return False
    finally:
        os.remove(tmp_path)

    slot.empty()
    st.session_state.songs.append(song)
    st.session_state.just_made = song["title"]
    return True


def render_song(song: dict, number: int) -> None:
    accent = SWATCHES[(number - 1) % len(SWATCHES)]
    title = html.escape(song["title"])
    path = song["audio_path"]

    with st.container(key=f"song_{number}"):
        st.markdown(
            f'<div class="song-head"><span class="swatch" style="background:{accent}"></span>'
            f'<div><div class="song-meta">Track {number}</div>'
            f'<div class="song-title">{title}</div></div></div>',
            unsafe_allow_html=True,
        )
        if not os.path.exists(path):
            st.warning("The audio file for this track is missing.")
            return

        player, save = st.columns([3, 1], vertical_alignment="center")
        player.audio(path)
        with open(path, "rb") as fh:
            save.download_button(
                "Download",
                data=fh.read(),
                file_name=f"{slugify(song['title'])}{os.path.splitext(path)[1] or '.wav'}",
                mime=mimetypes.guess_type(path)[0] or "audio/wav",
                key=f"dl_{number}",
            )
        with st.expander("Lyrics"):
            lyrics = html.escape(song["lyrics"]).replace("\n", "<br>")
            st.markdown(f'<div class="lyrics">{lyrics}</div>', unsafe_allow_html=True)


# ---------- hero ----------
st.markdown(
    '<div class="hero"><div class="brand"><div class="pads">'
    + "".join(f'<i style="background:{c}"></i>' for c in SWATCHES)
    + "</div><h1>Say-nthesizer</h1></div>"
    '<p class="tagline">Say a prompt. Hear a song. In your own voice.</p></div>',
    unsafe_allow_html=True,
)

left, right = st.columns([5, 6], gap="large")

# ---------- recorder ----------
with left:
    with st.container(key="recorder"):
        st.markdown(
            '<div class="panel-title">Record your idea</div>'
            '<div class="panel-sub">Press the mic, say what the song is about, then stop.</div>',
            unsafe_allow_html=True,
        )
        audio = st.audio_input(
            "Your song idea",
            key=f"rec_{st.session_state.rec_n}",
            label_visibility="collapsed",
        )
        st.markdown(
            '<div class="hint">Not sure what to say? Try one of these.</div><div class="chips">'
            + "".join(f'<span class="chip">{html.escape(x)}</span>' for x in EXAMPLES)
            + "</div>",
            unsafe_allow_html=True,
        )

        vibe_options = [
            "Chill & Genuine",
            "Playful & Quirky",
            "Sarcastic & Witty",
            "Ridiculous & Melodramatic",
            "Unhinged Chaos",
        ]
        selected_vibe = st.select_slider(
            "Vibe & Humor",
            options=vibe_options,
            value="Ridiculous & Melodramatic",
            help="Controls how exaggerated, silly, or serious the lyrics will be.",
        )

        status_slot = st.empty()
        go = st.button("Make my song", type="primary", disabled=audio is None)

        if go and audio is not None:
            if generate(audio, selected_vibe, status_slot):
                st.session_state.rec_n += 1  # clear the recorder for the next idea
                st.rerun()

# ---------- discography ----------
with right:
    songs = st.session_state.songs
    count = f'<span class="count">{len(songs)}</span>' if songs else ""
    st.markdown(f'<div class="section"><h2>Your discography</h2>{count}</div>', unsafe_allow_html=True)

    with st.container(key="discography"):
        if not songs:
            st.markdown(
                '<div class="empty">Nothing here yet. Record an idea and your first track will land here.</div>',
                unsafe_allow_html=True,
            )
        for i in range(len(songs), 0, -1):  # newest first
            render_song(songs[i - 1], i)