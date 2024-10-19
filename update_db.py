import sqlite3
import os
import pandas as pd

# Paths for local content
IMAGE_PATH = "./suno-ai-music-prompts/image"
AUDIO_PATH = "./suno-ai-music-prompts/audio"

# Load the language codes CSV
csv_file_path = "language-codes.csv"
language_codes_df = pd.read_csv(csv_file_path)  # Ensure the CSV is in the same folder

# Connect to the SQLite database
conn = sqlite3.connect('suno.db')
cursor = conn.cursor()

# Helper function to check if local files exist
def file_exists(song_id, content_type):
    path = f"{IMAGE_PATH}/{song_id}.jpeg" if content_type == "image" else f"{AUDIO_PATH}/{song_id}.mp3"
    return os.path.exists(path)

# Drop and recreate the json_data table with new boolean columns
cursor.execute('ALTER TABLE json_data RENAME TO json_data_old')
cursor.execute('''
    CREATE TABLE json_data (
        id TEXT PRIMARY KEY,
        title TEXT,
        meta_prompt_lang TEXT,
        model_name TEXT,
        meta_duration REAL,
        play_count INTEGER,
        meta_prompt TEXT,
        audio_url TEXT,
        image_url TEXT,
        local_image BOOLEAN DEFAULT FALSE,
        local_audio BOOLEAN DEFAULT FALSE
    )
''')

# Copy data from old table to new table with updated local file checks
rows = cursor.execute('SELECT id FROM json_data_old').fetchall()
data_to_insert = [(row[0], file_exists(row[0], "image"), file_exists(row[0], "audio")) for row in rows]

for row_id, local_image, local_audio in data_to_insert:
    cursor.execute('''
        INSERT INTO json_data (
            id, title, meta_prompt_lang, model_name, meta_duration, 
            play_count, meta_prompt, audio_url, image_url, local_image, local_audio
        )
        SELECT 
            id, title, meta_prompt_lang, model_name, meta_duration, 
            play_count, meta_prompt, audio_url, image_url, ?, ?
        FROM json_data_old
        WHERE id = ?
    ''', (local_image, local_audio, row_id))

# Drop the old table
cursor.execute('DROP TABLE json_data_old')

# Drop and recreate the languages table
cursor.execute('DROP TABLE IF EXISTS languages')
cursor.execute('''
    CREATE TABLE languages (
        language_code TEXT PRIMARY KEY,
        language TEXT,
        count INTEGER
    )
''')

# Drop and recreate the models table
cursor.execute('DROP TABLE IF EXISTS models')
cursor.execute('''
    CREATE TABLE models (
        model_name TEXT PRIMARY KEY,
        count INTEGER
    )
''')

# Populate the languages table with meta_prompt_lang and counts from json_data
cursor.execute('''
    INSERT OR REPLACE INTO languages (language_code, count)
    SELECT meta_prompt_lang AS language_code, COUNT(*) AS count
    FROM json_data
    WHERE meta_prompt_lang IS NOT NULL
    GROUP BY meta_prompt_lang
''')

# Load the languages from SQLite into a DataFrame to join with the CSV data
languages_df = pd.read_sql_query('SELECT * FROM languages', conn)

# Join the languages table with the language codes CSV to add the full language name
merged_df = pd.merge(
    languages_df, language_codes_df,
    how='left', left_on='language_code', right_on='alpha2'
).drop(columns=['alpha2'])  # Drop the redundant CSV column

# Insert the updated data with full language names back into the languages table
cursor.executemany(
    'UPDATE languages SET language = ? WHERE language_code = ?',
    [(row['English'], row['language_code']) for _, row in merged_df.iterrows()]
)

# Populate the models table with unique model_name values and their counts
cursor.execute('''
    INSERT OR REPLACE INTO models (model_name, count)
    SELECT model_name, COUNT(*) AS count
    FROM json_data
    WHERE model_name IS NOT NULL
    GROUP BY model_name
''')

# Commit the changes and close the connection
conn.commit()

# Optional: Display the contents of the languages and models tables for verification
print("Languages Table:")
cursor.execute("SELECT * FROM languages")
print(cursor.fetchall())

print("\nModels Table:")
cursor.execute("SELECT * FROM models")
print(cursor.fetchall())

# Close the database connection
conn.close()
