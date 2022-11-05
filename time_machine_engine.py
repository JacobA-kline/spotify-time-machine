import datetime
import os
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth

DATE = ""


def get_user_date():
    global DATE
    DATE = input("Which year would you like to travel to? "
                 "Please type the date in the following format: YYYY-MM-DD\n")
    try:
        datetime.datetime.strptime(DATE, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")


SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_SECRET = os.environ.get("SPOTIFY_SECRET")


sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="https://localhost:8888/callback",
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_SECRET,
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]


def scraping():
    """Scraping billboard.com for songs from specific date and adding to a list"""
    response = requests.get(f"https://www.billboard.com/charts/hot-100/{DATE}")
    website_html = response.text
    soup = BeautifulSoup(website_html, "html.parser")
    h3 = soup.find_all(name="h3", class_="a-no-trucate")

    song_list = []
    for song in h3:
        song = song.getText().strip()
        song_list.append(song)
    return song_list


def create_new_playlist():
    """Create a new playlist"""
    playlist = sp.user_playlist_create(user=user_id, name=f"{DATE} Billboard 100",
                                       public=False, collaborative=False,
                                       description=f"A playlist of the top 100 from {DATE}")
    add_songs_playlist(playlist_id=playlist['id'])


def add_songs_playlist(playlist_id):
    """Adding songs from song list to the spotify playlist"""
    count = 0
    song_uri_list = []
    for song in scraping():
        if not sp.search(q=song)['tracks']['items']:
            count += 1
            print(f"Sorry, {count} song/s can't be found in Spotify.")
            continue
        else:
            song_uri = sp.search(q=song)['tracks']["items"][0]["uri"]
            song_uri_list.append(song_uri)
    sp.playlist_add_items(playlist_id=playlist_id, items=song_uri_list)
