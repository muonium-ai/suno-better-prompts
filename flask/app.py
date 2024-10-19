from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import sqlite3

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///suno.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the models for the JSON data, languages, and models
class Song(db.Model):
    __tablename__ = 'json_data'
    id = db.Column(db.Text, primary_key=True)
    title = db.Column(db.Text)
    meta_prompt_lang = db.Column(db.Text)
    model_name = db.Column(db.Text)
    meta_duration = db.Column(db.Float)
    play_count = db.Column(db.Integer)
    meta_prompt = db.Column(db.Text)
    audio_url = db.Column(db.Text)
    image_url = db.Column(db.Text)

class Language(db.Model):
    __tablename__ = 'languages'
    language_code = db.Column(db.Text, primary_key=True)
    language = db.Column(db.Text)
    count = db.Column(db.Integer)

class Model(db.Model):
    __tablename__ = 'models'
    model_name = db.Column(db.Text, primary_key=True)
    count = db.Column(db.Integer)

# Create the tables if they don't exist
def initialize_db():
    with sqlite3.connect('../suno.db') as conn:
        cursor = conn.cursor()
        # Create languages table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS languages (
                language_code TEXT PRIMARY KEY,
                language TEXT,
                count INTEGER
            )
        ''')
        # Create models table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS models (
                model_name TEXT PRIMARY KEY,
                count INTEGER
            )
        ''')
        conn.commit()

# @app.before_first_request
def setup():
    """Ensure tables are initialized before the first request."""
    initialize_db()

# Route for the index page with search functionality
@app.route('/', methods=['GET', 'POST'])
def index():
    search_query = request.form.get('search_query', '')
    selected_language = request.form.get('language', '')
    selected_model = request.form.get('model', '')

    # Query for languages and models to populate the dropdowns
    languages = Language.query.all()
    models = Model.query.all()

    # Build the query dynamically based on filters
    query = Song.query
    if search_query:
        query = query.filter(
            (Song.title.ilike(f'%{search_query}%')) |
            (Song.meta_prompt.ilike(f'%{search_query}%'))
        )
    if selected_language:
        query = query.filter(Song.meta_prompt_lang == selected_language)
    if selected_model:
        query = query.filter(Song.model_name == selected_model)

    # Execute the query and fetch results
    songs = query.all()

    return render_template(
        'index.html',
        songs=songs,
        languages=languages,
        models=models,
        search_query=search_query,
        selected_language=selected_language,
        selected_model=selected_model
    )

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
