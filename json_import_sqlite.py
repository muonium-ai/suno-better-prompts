import os
import json
import sqlite3
from pathlib import Path
import sys
import time

def create_table(cursor):
    """
    Create the SQLite table with hard-coded metadata fields.
    """
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS json_data (
            id TEXT PRIMARY KEY,
            video_url TEXT,
            audio_url TEXT,
            image_url TEXT,
            image_large_url TEXT,
            is_video_pending BOOLEAN,
            major_model_version TEXT,
            model_name TEXT,
            reaction TEXT,
            display_name TEXT,
            handle TEXT,
            is_handle_updated BOOLEAN,
            avatar_image_url TEXT,
            is_following_creator BOOLEAN,
            user_id TEXT,
            created_at TEXT,
            status TEXT,
            title TEXT,
            play_count INTEGER,
            upvote_count INTEGER,
            is_public BOOLEAN,
            meta_tags TEXT,
            meta_negative_tags TEXT,
            meta_prompt TEXT,
            meta_audio_prompt_id TEXT,
            meta_history TEXT,
            meta_concat_history TEXT,
            meta_stem_from_id TEXT,
            meta_type TEXT,
            meta_duration REAL,
            meta_refund_credits BOOLEAN,
            meta_stream BOOLEAN,
            meta_infill TEXT,
            meta_has_vocal BOOLEAN,
            meta_is_audio_upload_tos_accepted BOOLEAN,
            meta_error_type TEXT,
            meta_error_message TEXT,
            meta_configurations TEXT,
            meta_artist_clip_id TEXT,
            meta_cover_clip_id TEXT,
            meta_prompt_lang TEXT,
            meta_gpt_lang TEXT
        )
    ''')

def insert_json_data(cursor, data):
    """
    Insert the JSON data into the SQLite database.
    """
    metadata = data.get('metadata', {})

    # Convert lists/dicts to JSON strings
    def to_json_string(value):
        if isinstance(value, (list, dict)):
            return json.dumps(value)  # Convert to JSON string
        return value

    # Prepare the values for insertion
    values = [
        data.get('id'),
        data.get('video_url'),
        data.get('audio_url'),
        data.get('image_url'),
        data.get('image_large_url'),
        data.get('is_video_pending'),
        data.get('major_model_version'),
        data.get('model_name'),
        data.get('reaction'),
        data.get('display_name'),
        data.get('handle'),
        data.get('is_handle_updated'),
        data.get('avatar_image_url'),
        data.get('is_following_creator'),
        data.get('user_id'),
        data.get('created_at'),
        data.get('status'),
        data.get('title'),
        data.get('play_count'),
        data.get('upvote_count'),
        data.get('is_public'),
        metadata.get('tags'),
        metadata.get('negative_tags', None),
        metadata.get('prompt', None),
        metadata.get('audio_prompt_id', None),
        to_json_string(metadata.get('history', None)),  # Handle list
        to_json_string(metadata.get('concat_history', None)),  # Handle list
        metadata.get('stem_from_id', None),
        metadata.get('type', None),
        metadata.get('duration', None),
        metadata.get('refund_credits', None),
        metadata.get('stream', None),
        metadata.get('infill', None),
        metadata.get('has_vocal', None),
        metadata.get('is_audio_upload_tos_accepted', None),
        metadata.get('error_type', None),
        metadata.get('error_message', None),
        metadata.get('configurations', None),
        metadata.get('artist_clip_id', None),
        metadata.get('cover_clip_id', None),
        metadata.get('prompt_lang', None),
        metadata.get('gpt_lang', None)
    ]

    # Insert the data into the table
    cursor.execute(f'''
        INSERT OR IGNORE INTO json_data (
            id, video_url, audio_url, image_url, image_large_url,
            is_video_pending, major_model_version, model_name, reaction,
            display_name, handle, is_handle_updated, avatar_image_url,
            is_following_creator, user_id, created_at, status, title,
            play_count, upvote_count, is_public,
            meta_tags, meta_negative_tags, meta_prompt, meta_audio_prompt_id,
            meta_history, meta_concat_history, meta_stem_from_id, meta_type,
            meta_duration, meta_refund_credits, meta_stream, meta_infill,
            meta_has_vocal, meta_is_audio_upload_tos_accepted, meta_error_type,
            meta_error_message, meta_configurations, meta_artist_clip_id,
            meta_cover_clip_id, meta_prompt_lang, meta_gpt_lang
        ) VALUES ({", ".join(["?"] * len(values))})
    ''', values)

def process_file(cursor, file_path):
    """
    Process a single JSON file and insert its data into the database.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        insert_json_data(cursor, data)

def process_folder(cursor, folder_path):
    """
    Process all JSON files in the given folder.
    """
    for file in Path(folder_path).glob('*.json'):
        print(f"Processing {file}")
        process_file(cursor, file)

def main(input_path):
    """
    Main function to handle the SQLite connection and input path.
    """
    start_time = time.time()  # Track start time
    conn = sqlite3.connect('json_data.db')
    cursor = conn.cursor()

    # Create the table
    create_table(cursor)

    # Process input path (file or folder)
    if os.path.isfile(input_path):
        process_file(cursor, input_path)
    elif os.path.isdir(input_path):
        process_folder(cursor, input_path)
    else:
        print("Invalid input path. Please provide a valid file or folder.")
        conn.close()
        return

    # Commit changes
    conn.commit()

    # Get total records inserted
    cursor.execute("SELECT COUNT(*) FROM json_data")
    total_records = cursor.fetchone()[0]

    # Close the connection
    conn.close()

    # Calculate total running time
    end_time = time.time()
    total_time = end_time - start_time

    print(f"Data import completed.")
    print(f"Total records inserted: {total_records}")
    print(f"Total running time: {total_time:.2f} seconds")

if __name__ == '__main__':
    # Ensure the path is provided as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python import_json_sqlite.py <path_to_json_file_or_folder>")
        sys.exit(1)

    input_path = sys.argv[1]
    main(input_path)
