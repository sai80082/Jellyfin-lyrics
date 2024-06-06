import re
import os
from difflib import SequenceMatcher
import logging
from tinytag import TinyTag
import os
import requests
# Configure logging
logging.basicConfig(filename='lyrics_fetch.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

directory_path = '/home/serveradmin/media/music'
def search_song_netease(keyword):
    api_url = f"https://music.163.com/api/search/get?s={keyword}&type=1&limit=50"
    response = requests.get(api_url)
    if response.status_code != 200:
        return None
    return response.json().get('result')

def download_lyrics_netease(song_id):
    url = "https://music.163.com/api/song/lyric"
    params = {"tv": "-1", "lv": "-1", "kv": "-1", "id": song_id}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None, None
    data = response.json()
    lrc = data.get('lrc', {}).get('lyric', '')
    tlyric = data.get('tlyric', {}).get('lyric', '')
    return lrc, tlyric

def parse_lyrics_netease(lyrics):
    lyrics_dict = {}
    unformatted_lines = []
    pattern = re.compile(r'\[(\d{2}):(\d{2})([.:]\d{2,3})?\](.*)')
    for line in lyrics.split('\n'):
        match = pattern.match(line)
        if match:
            minute, second, millisecond, lyric = match.groups()
            millisecond = millisecond if millisecond else '.000'
            millisecond = millisecond.replace(':', '.')
            time_stamp = f"[{minute}:{second}{millisecond}]"
            lyrics_dict[time_stamp] = lyric
        else:
            unformatted_lines.append(line)
    return lyrics_dict, unformatted_lines

def merge_lyrics_netease(lrc_dict, tlyric_dict, unformatted_lines):
    merged_lyrics = unformatted_lines
    all_time_stamps = sorted(set(lrc_dict.keys()).union(tlyric_dict.keys()))
    for time_stamp in all_time_stamps:
        original_line = lrc_dict.get(time_stamp, '')
        translated_line = tlyric_dict.get(time_stamp, '')
        merged_lyrics.append(f"{time_stamp}{original_line}")
        if translated_line:
            merged_lyrics.append(f"{time_stamp}{translated_line}")
    return '\n'.join(merged_lyrics)

def get_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def get_lyrics_netease(artist, title, album, duration):
    search_keywords = [
        f"{artist} - {album} - {title}",
        f"{album} - {title}",
        f"{artist} - {title}"
    ]

    results = []

    for keyword in search_keywords:
        search_result = search_song_netease(keyword)
        if not search_result:
            continue

        songs = search_result.get('songs', [])
        songs = [song for song in songs if abs(song['duration'] / 1000 - duration) <= 3]

        for song in songs[:3]:
            lyrics_content, trans_lyrics_content = download_lyrics_netease(song['id'])

            if lyrics_content:
                lrc_dict, unformatted_lines = parse_lyrics_netease(lyrics_content)
                if len(lrc_dict) >= 5:
                    tlyric_dict, _ = parse_lyrics_netease(trans_lyrics_content if trans_lyrics_content else '')
                    merged = merge_lyrics_netease(lrc_dict, tlyric_dict, unformatted_lines)
                    similarity = (
                        get_similarity(title, song['name']) +
                        get_similarity(artist, ', '.join([artist['name'] for artist in song['artists']])) +
                        get_similarity(album, song.get('album', {}).get('name', ''))
                    ) / 3
                    results.append({
                        "id": str(song['id']),
                        "title": song['name'],
                        "artist": ', '.join([artist['name'] for artist in song['artists']]),
                        "lyrics": merged,
                        "similarity": similarity
                    })

    if not results:
        return None

    results.sort(key=lambda x: x['similarity'], reverse=True)
    top_result = results[0] if results else None

    if top_result and top_result['similarity'] >= 0.33:
        return top_result['lyrics']
    else:
        return None

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
    return response.json()["syncedLyrics"].encoding('utf-8')

def get_song_details(file_path):
    audio = TinyTag.get(file_path)
    return audio.album, audio.title, audio.artist, int(audio.duration)

def collect_audio_files(directory_path):
    audio_files = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(('.flac', '.mp3', '.wav', '.ogg', '.aac', '.wma')):
                audio_files.append(os.path.join(root, file))
    return audio_files

Found_lyrics = 0
Missing_lyrics = 0
Total_lyrics = 0
print("Starting the lyrics fetching process...")
print("Writing logs to lyrics_fetch.log")

try:
    audio_files = collect_audio_files(directory_path)
    total_files = len(audio_files)
    for idx, file_path in enumerate(audio_files, start=1):
        logging.info("Processing file %s of %s - %s", idx, total_files, file_path)
        new_file_path = os.path.splitext(file_path)[0] + '.lrc'
        if os.path.exists(new_file_path):
            logging.info("Lyrics already exist for the song: %s", file_path)
            continue
        try:
            album, title, artist, duration = get_song_details(file_path)
            try:
                lyrics = get_lyrics(artist, title, album, duration)
            except Exception as e:
                lyrics = get_lyrics_netease(artist, title, album, duration)
        except Exception as e:
            print("error!")
            logging.error("Error in fetching lyrics for the song: %s", file_path)
            Missing_lyrics = Missing_lyrics + 1
            continue
        try:
            if (lyrics is  None):
                logging.info("Lyrics not found for the song: %s", file_path)
                Missing_lyrics = Missing_lyrics + 1
                continue
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
