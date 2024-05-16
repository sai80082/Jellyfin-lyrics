import logging
from tinytag import TinyTag
import os
import requests

# Configure logging
logging.basicConfig(filename='lyrics_fetch.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

directory_path = '/home/serveradmin/media/music'

def get_lyrics(artist, title, album, duration):
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

Found_lyrics = 0
Missing_lyrics = 0
print("Starting the lyrics fetching process...")
print("Writing logs to lyrics_fetch.log")

try:
    flac_files = collect_flac_files(directory_path)
    total_files = len(flac_files)
    for idx, file_path in enumerate(flac_files, start=1):
        logging.info("Processing file %s of %s - %s", idx, total_files, file_path)
        new_file_path = os.path.splitext(file_path)[0] + '.lrc'
        if os.path.exists(new_file_path):
            logging.info("Lyrics already exist for the song: %s", file_path)
            continue
        try:
            album, title, artist, duration = get_song_details(file_path)
            lyrics = get_lyrics(artist, title, album, duration)
        except Exception as e:
            logging.error("Error in fetching lyrics for the song: %s", file_path)
            Missing_lyrics = Missing_lyrics + 1
            continue
        try:
            with open(new_file_path, 'w') as f:
                f.write(lyrics)
                Total_lyrics = Total_lyrics + 1
        except Exception as e:
            logging.error("Error in writing lyrics for the song: %s", file_path)
            continue
except KeyboardInterrupt:
    logging.info("Exiting the program due to keyboard interrupt")
    exit(0)


print("Total songs processed:", total_files)
print("Total songs with lyrics found:", Found_lyrics)
print("Total songs with lyrics missing:", Missing_lyrics)
print("Check the log file for more details.")
print("Logging file path:", os.path.abspath('lyrics_fetch.log'))