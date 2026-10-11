"""Streamlit UI (Person A). Run with:  streamlit run app.py"""
import os
import tempfile

import streamlit as st

from pipeline import make_song

st.set_page_config(page_title="Say-nthesizer", layout="centered")

# Streamlit reruns this whole script on every click, so keep results in session_state.
if "songs" not in st.session_state:
    st.session_state.songs = []  # discography for this session

st.title("Say-nthesizer")
st.caption("Say a prompt. Hear a song. In your own voice.")

audio = st.audio_input("Say your song idea (e.g. 'a power ballad about my flatmate stealing my oat milk')")

if audio is not None and st.button("Make my song", type="primary"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio.getvalue())
        tmp_path = f.name
    with st.spinner("Booking the studio..."):
        try:
            st.session_state.songs.append(make_song(tmp_path))
        except Exception as e:
            st.error(f"Studio is on fire: {e}")
        finally:
            os.remove(tmp_path)

for song in reversed(st.session_state.songs):
    st.subheader(song["title"])
    st.audio(song["audio_path"])
    with st.expander("Lyrics"):
        st.text(song["lyrics"])
