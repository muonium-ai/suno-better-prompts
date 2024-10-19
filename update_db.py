import sqlite3
import pandas as pd

# Load the language codes CSV
csv_file_path = "language-codes.csv"
language_codes_df = pd.read_csv(csv_file_path)  # Ensure the CSV is in the same folder

# Connect to the SQLite database
conn = sqlite3.connect('suno.db')
cursor = conn.cursor()

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

# Optional: Display the contents of both tables for verification
print("Languages Table:")
cursor.execute("SELECT * FROM languages")
print(cursor.fetchall())

print("\nModels Table:")
cursor.execute("SELECT * FROM models")
print(cursor.fetchall())

# Close the database connection
conn.close()
