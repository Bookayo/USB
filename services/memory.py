"""Discography memory (Person C). Optional: do this last, once the main flow works.

Right now it just keeps songs in a local list so pipeline.py has something to call.
TODO: swap in OpenLoft (check their docs) so the app remembers past songs between
sessions and can call back to them ("back for another one after 'Oat Milk Betrayal'?").
"""

_songs = []


def remember_song(song: dict) -> None:
    _songs.append({"title": song["title"], "transcript": song.get("transcript", "")})


def recall_songs() -> list:
    return list(_songs)
