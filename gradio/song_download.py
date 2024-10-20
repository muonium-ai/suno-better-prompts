import sqlite3
import sys
import os
import requests

# Constants
DB_PATH = '../suno.db'  # Adjust the path to your SQLite database
DOWNLOAD_FOLDER = "./downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)  # Ensure download folder exists

def get_db_connection():
    """Connect to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Get rows as dictionaries
    return conn

def fetch_songs(search_query, limit):
    """Query the database for songs matching the search query."""
    conn = get_db_connection()

    query = """
        SELECT id, title, audio_url, image_url, local_audio, local_image
        FROM json_data
        WHERE title LIKE ? OR meta_prompt LIKE ?
        LIMIT ?
    """
    params = [f'%{search_query}%', f'%{search_query}%', limit]
    songs = conn.execute(query, params).fetchall()
    conn.close()

    return songs

def human_readable_size(size_in_bytes):
    """Convert bytes to KB, MB, or GB."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} Bytes"
    elif size_in_bytes < 1024**2:
        return f"{size_in_bytes / 1024:.2f} KB"
    elif size_in_bytes < 1024**3:
        return f"{size_in_bytes / (1024**2):.2f} MB"
    else:
        return f"{size_in_bytes / (1024**3):.2f} GB"

def download_file(url, filename):
    """Download a file from a given URL if it doesn't already exist."""
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)

    # Check if file already exists
    if os.path.exists(file_path):
        print(f"File exists: {filename}")
        return None

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad status codes

        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = os.path.getsize(file_path)
        print(f"Downloaded: {filename} ({human_readable_size(file_size)})")
        return file_path
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {filename}: {e}")
        return None

def download_song_assets(song):
    """Download both audio and image for a song."""
    song_id = song["id"]

    # Determine URLs (can be local or remote)
    audio_url = song["audio_url"]
    image_url = song["image_url"]

    # Download the audio and image files
    audio_filename = f"{song_id}.mp3"
    image_filename = f"{song_id}.jpeg"

    download_file(audio_url, audio_filename)
    download_file(image_url, image_filename)

def main():
    """Main function to parse arguments and download songs."""
    if len(sys.argv) < 3:
        print("Usage: python song_downloader.py <search_query> <number_of_songs>")
        sys.exit(1)

    # Parse arguments
    search_query = sys.argv[1]
    number_of_songs = int(sys.argv[2])

    # Fetch songs from the database
    songs = fetch_songs(search_query, number_of_songs)

    if not songs:
        print("No songs found matching your search criteria.")
        sys.exit(0)

    # Download assets for each song
    for song in songs:
        print(f"Downloading assets for: {song['title']}")
        download_song_assets(song)

    print("Download completed.")

if __name__ == "__main__":
    main()
