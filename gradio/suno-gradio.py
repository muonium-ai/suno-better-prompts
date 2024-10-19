import sqlite3
import gradio as gr
import signal
import sys

# Flask server URL to serve static files
FLASK_SERVER_URL = "http://127.0.0.1:5000"

# Connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('../suno.db')  # Database path
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

# Fetch unique languages and models for dropdown options
def get_filter_options():
    conn = get_db_connection()
    languages = conn.execute("SELECT DISTINCT meta_prompt_lang FROM json_data").fetchall()
    models = conn.execute("SELECT DISTINCT model_name FROM json_data").fetchall()
    conn.close()

    # Prepare dropdown options (including "All")
    language_options = ["All"] + [lang["meta_prompt_lang"] for lang in languages if lang["meta_prompt_lang"]]
    model_options = ["All"] + [model["model_name"] for model in models if model["model_name"]]
    
    return language_options, model_options

# Query the database and prepare the output based on filters
def search_songs(search_query, selected_language, selected_model, local_only):
    conn = get_db_connection()

    # Build the query dynamically based on user filters
    query = """
        SELECT id, title, meta_prompt AS lyrics, meta_duration AS duration, 
               play_count, meta_prompt_lang AS language, model_name, 
               audio_url, image_url, local_image, local_audio
        FROM json_data
        WHERE (title LIKE ? OR meta_prompt LIKE ?)
    """
    params = [f'%{search_query}%', f'%{search_query}%']

    # Add language filter if selected
    if selected_language != "All":
        query += " AND meta_prompt_lang = ?"
        params.append(selected_language)

    # Add model filter if selected
    if selected_model != "All":
        query += " AND model_name = ?"
        params.append(selected_model)

    # Add local content filter if checked
    if local_only:
        query += " AND local_audio = 1"

    query += " ORDER BY play_count DESC LIMIT 20"
    results = conn.execute(query, params).fetchall()
    conn.close()

    if not results:
        return "No songs found matching your search criteria."

    # Prepare the formatted HTML output
    formatted_results = ""
    for row in results:
        image_origin = "Local Content" if row["local_image"] else "Server Content"
        audio_origin = "Local Content" if row["local_audio"] else "Server Content"

        image_url = (
            f"{FLASK_SERVER_URL}/images/{row['id']}.jpeg"
            if row["local_image"] else row["image_url"]
        )
        audio_url = (
            f"{FLASK_SERVER_URL}/audio/{row['id']}.mp3"
            if row["local_audio"] else row["audio_url"]
        )

        formatted_results += f"""
        <h2>{row['title']}</h2>
        <p><strong>Language:</strong> {row['language']} | <strong>Model:</strong> {row['model_name']}</p>
        <p><strong>Duration:</strong> {row['duration']} seconds | <strong>Play Count:</strong> {row['play_count']}</p>
        <p><strong>Lyrics:</strong><br>{row['lyrics']}</p>

        <p><strong>Image Source:</strong> <b>{image_origin}</b></p>
        <img src="{image_url}" alt="Song Image" width="300"><br>

        <p><strong>Audio Source:</strong> <b>{audio_origin}</b></p>
        <audio controls>
            <source src="{audio_url}" type="audio/mpeg">
            Your browser does not support the audio element.
        </audio>
        <hr>
        """

    return formatted_results

# Fetch filter options for the dropdowns
language_options, model_options = get_filter_options()

# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("# Song Search")

    with gr.Row():
        search_query = gr.Textbox(label="Search by Title or Lyrics", placeholder="Enter search term...")

    with gr.Row():
        language_dropdown = gr.Dropdown(choices=language_options, label="Select Language", value="All")
        model_dropdown = gr.Dropdown(choices=model_options, label="Select Model", value="All")

    local_content_checkbox = gr.Checkbox(label="Local Content Only", value=False)

    search_button = gr.Button("Search")
    output = gr.HTML()

    # Connect the search button to the search function
    search_button.click(
        search_songs, 
        inputs=[search_query, language_dropdown, model_dropdown, local_content_checkbox], 
        outputs=output
    )

    # Signal handler to handle termination gracefully
    def handle_sigterm(*args):
        print("Gradio app is shutting down...")
        sys.exit(0)

    # Register the signal handler
    signal.signal(signal.SIGTERM, handle_sigterm)

# Run the Gradio app
if __name__ == "__main__":
    demo.launch(server_port=7860)
