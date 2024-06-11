import logging, os, functions
from time import sleep
from alive_progress import alive_bar

# Configure logging
logging.basicConfig(filename='lyrics_fetch.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

print('\n:::::::::::::::::::: WELCOME ::::::::::::::::::::\n')

directory_path = input('Enter folder path: ')
directory_path = functions.replaces(directory_path)

print(f'\nSearching files in: {directory_path}')

Found_lyrics, Missing_lyrics, Already_founds, Total_lyrics = 0, 0, 0, 0

print("Starting the lyrics fetching process...")
print("Writing logs to lyrics_fetch.log")
print('------------------------------------------------- \n')

try:
    audio_files = functions.collect_audio_files(directory_path)
    total_files = len(audio_files)
    with alive_bar(total_files, bar = 'smooth', stats = True, title = 'Processing: ') as bar:
        for idx, file_path in enumerate(audio_files, start=1):
            logging.info("Processing file %s of %s - %s", idx, total_files, file_path)
            new_file_path = os.path.splitext(file_path)[0] + '.lrc'
            if os.path.exists(new_file_path):
                logging.info("Lyrics already exist for the song: %s", file_path)
                Already_founds = Already_founds + 1
                continue
            try:
                album, title, artist, duration = functions.get_song_details(file_path)
                lyrics = functions.get_lyrics(artist, title, album, duration)
            except Exception as e:
                logging.error("Error in fetching lyrics for the song: %s", file_path)
                Missing_lyrics = Missing_lyrics + 1
                continue
            try:
                if (lyrics is  None):
                    logging.info("Lyrics not found for the song: %s", file_path)
                    Missing_lyrics = Missing_lyrics + 1
                    continue
                with open(new_file_path, 'w') as f:
                    f.write(lyrics.decode('utf-8'))
                    Total_lyrics = Total_lyrics + 1
            except Exception as e:
                logging.error("Error in writing lyrics for the song: %s", file_path)
                print(e)
                continue
            sleep(0.01)
            bar()
except KeyboardInterrupt:
    logging.info("Exiting the program due to keyboard interrupt")
    exit(0)

Found_lyrics = total_files - Missing_lyrics
percentage = round((Found_lyrics/total_files)*100, 2)

print('-------------------------------------------------')
print(f"Total songs processed:{total_files - Already_founds}")
print(f"Total songs with lyrics found: {Found_lyrics}")
print(f"Total songs with lyrics previously downloaded: {Already_founds}")
print(f"Total songs with lyrics missing: {Missing_lyrics}")
print(f"Efficiency: {percentage} % \n")
print('------------------------------------------------- \n')
print("Check the log file for more details.")
print("Logging file path:", os.path.abspath('lyrics_fetch.log'))