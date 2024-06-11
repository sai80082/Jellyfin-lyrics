import logging
import requests
import os
from tinytag import TinyTag

def get_lyrics(artist, title, album, duration):
    """Sumary: Function that fetch lyrics from lrclib

    Args:
        artist (string): artist name
        title (string): song title
        album (string): album title
        duration (float): duration (in seconds)

    Returns:
        list: list with file attributes
    """
    url = "https://lrclib.net/api/get"
    params = {
        "artist_name": artist,
        "track_name": title,
        "album_name": album,
        "duration": duration
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        logging.info("Found Lyrics for the song: %s", title)
    return response.json()["syncedLyrics"].encode('utf-8')

def get_song_details(file_path):
    """Extract params from audio file

    Args:
        file_path (string): path of audio file

    Returns:
        tuple: params of audio file
    """
    audio = TinyTag.get(file_path)
    return audio.album, audio.title, audio.artist, int(audio.duration)

def collect_audio_files(directory_path):
    """Collects audio file in directory

    Args:
        directory_path (string): directory where you store your audio files

    Returns:
        list: a collection of the paths of each audio file in your directory
    """
    audio_files = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(('.flac', '.mp3', '.wav', '.ogg', '.aac', '.wma')):
                audio_files.append(os.path.join(root, file))
    return audio_files

def replaces(directory):
    """For windows enviroments. Replaces "\\" with "/"

    Args:
        directory (string): the path of your audio files directory

    Returns:
        string: directory path with "/" instead of "\\"
    """
    folder_path = directory.replace("\\","/")
    return folder_path