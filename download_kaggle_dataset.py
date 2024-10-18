import opendatasets as od
from datetime import datetime

print("Downloading the dataset...")

# Record the start time
start_time = datetime.now()
print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

songs_dataset = "https://www.kaggle.com/datasets/rafyaa/suno-ai-music-prompts"
od.download(songs_dataset)

# Record the end time
end_time = datetime.now()
print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

# Calculate the time taken
time_taken = end_time - start_time
print(f"Time taken to download: {time_taken}")

print("Download complete.")