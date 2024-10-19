import sqlite3
import gradio as gr

# Connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('../suno.db')  # Updated path to '../suno.db'
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

# Query the database based on search input and order by play count
def search_songs(search_query):
    conn = get_db_connection()
    
    query = """
        SELECT title, meta_prompt AS lyrics, meta_duration AS duration, 
               play_count, meta_prompt_lang AS language, model_name, 
               audio_url, image_url 
        FROM json_data
        WHERE title LIKE ? OR meta_prompt LIKE ?
        ORDER BY play_count DESC
    """
    params = [f'%{search_query}%', f'%{search_query}%']
    results = conn.execute(query, params).fetchall()
    conn.close()

    # Display total results count
    total_count = len(results)
    if total_count == 0:
        return "No songs found matching your search criteria."

    # Limit to the first 20 results
    limited_results = results[:20]

    # Format results for display
    formatted_results = f"### Total Results: {total_count}\n\n"
    for row in limited_results:
        formatted_results += f"### {row['title']}\n"
        formatted_results += f"**Language:** {row['language']} | **Model:** {row['model_name']} | **Duration:** {row['duration']} seconds | **Play Count:** {row['play_count']}\n\n"
        formatted_results += f"**Lyrics:** {row['lyrics']}\n\n"
        formatted_results += f"![Image]({row['image_url']})\n\n"
        formatted_results += f'<audio controls><source src="{row["audio_url"]}" type="audio/mpeg">Your browser does not support the audio element.</audio>\n\n'
        formatted_results += "---\n"

    return formatted_results

# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("# Song Search")
    
    with gr.Row():
        search_query = gr.Textbox(label="Search by Title or Lyrics", placeholder="Enter search term...")
    
    search_button = gr.Button("Search")
    output = gr.Markdown()

    # Connect the search button to the search function
    search_button.click(
        search_songs, 
        inputs=[search_query], 
        outputs=output
    )

# Run the Gradio app
if __name__ == "__main__":
    demo.launch()
