from tinytag import TinyTag 
import os

directory_path = '/home/serveradmin/media/music'

def get_lyrics(artist, title, album, duration):
    import requests

    url = "https://lrclib.net/api/get"
    params = {
        "artist_name": artist,
        "track_name": title,
        "album_name": album,
        "duration": duration
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("Found Lyrics for the song:",title)
    return response.json()["syncedLyrics"]

def get_song_details(file_path):
    audio = TinyTag.get(file_path)
    return audio.album, audio.title, audio.artist, int(audio.duration)

def collect_flac_files(directory_path):
    flac_files = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.flac'):
                flac_files.append(os.path.join(root, file))
    return flac_files

try:
    flac_files = collect_flac_files(directory_path)
    total_files = len(flac_files)
    for idx, file_path in enumerate(flac_files, start=1):
        print("Processing file", idx, "of", total_files, "-", file_path)
        new_file_path = os.path.splitext(file_path)[0] + '.lrc'
        if os.path.exists(new_file_path):
            print("Lyrics already exist for the song:", file_path)
            continue
        try:
            album, title, artist, duration = get_song_details(file_path)
            lyrics = get_lyrics(artist, title, album, duration)
        except:
            print("Error in fetching lyrics for the song:", file_path)
            continue
        try:
            with open(new_file_path, 'w') as f:
                f.write(lyrics)
        except:
            print("Error in writing lyrics for the song:", file_path)
            continue
# keyboard interrupt
except KeyboardInterrupt:
    print("Exiting the program")
    exit(0)
