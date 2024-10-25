import sqlite3
import os
import re

# Connect to the SQLite database
conn = sqlite3.connect('suno.db')
cursor = conn.cursor()

# add column prompt_template to table
#cursor.execute('ALTER TABLE json_data ADD COLUMN prompt_template TEXT')
#cursor.execute('ALTER TABLE json_data ADD COLUMN template_length INTEGER')
# find all the rows and iterate through them
rows = cursor.execute('SELECT id, meta_prompt FROM json_data').fetchall()
for row in rows:
    # get the id and meta_prompt
    song_id, meta_prompt = row
    # find the prompt_template
    instructions = re.findall(r'\[(.*?)\]', meta_prompt)
    # update the prompt_template column
    # Remove empty strings and strip whitespace
    instructions = [instr.strip() for instr in instructions if instr.strip()]
    template_length = len(instructions)
    prompt_template =  "\n".join([f"[{instruction}]" for instruction in instructions])
    cursor.execute('''
        UPDATE json_data
        SET prompt_template = ?,
        template_length = ?
        WHERE id = ?
    ''', (prompt_template,template_length, song_id))
    print(f"{song_id}\n{template_length}\n{prompt_template}\n\n")

"""
# Find all strings inside square brackets
        instructions = re.findall(r'\[(.*?)\]', content)

        # Remove empty strings and strip whitespace
        instructions = [instr.strip() for instr in instructions if instr.strip()]

        # If content has more than min_instructions valid instructions, print only the instructions and filename
        if len(instructions) > min_instructions:
            output_lines.append(f"Filename: {filename}")
            print(f"Filename: {filename}")
            output_lines.append("Instructions:")
            print("Instructions:")
            for instr in instructions:
                output_lines.append(f"[{instr}]")
                print(f"[{instr}]")
            output_lines.append("")  # Add a newline for readability
            print("")  # Add a newline for readability

"""