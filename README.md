
# Suno Better Prompts

This project aims to determine which prompts perform better with Suno AI, using a Kaggle dataset along with supporting code.

## Step 1: Download the Dataset
The dataset is over 100GB and comes in a compressed format. Make sure you have at least **200GB of free space** available for both downloading and extraction.

[Kaggle Dataset: Suno AI Music Prompts](https://www.kaggle.com/datasets/rafyaa/suno-ai-music-prompts)

---

## Step 2: Create a Kaggle API Key
1. If you don't already have a Kaggle account, create one here: [Kaggle](https://www.kaggle.com/)
2. Generate an API key by navigating to your [Kaggle Account Settings](https://www.kaggle.com/settings).
3. Download the `kaggle.json` token and **save it in the project repository**.

---

## Step 3: Set Up Python Environment
1. Create a new Conda environment:
   ```bash
   conda create -n suno -y
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Step 4: Download the Dataset Using the API
Use the following command to download the dataset:
```bash
python download_kaggle_dataset.py
```

---

## Step 5: Unzip the Dataset
Extract the dataset into a folder named `suno-ai-music-prompts`.

The directory structure should look like this:
```
suno-ai-music-prompts/
├── audio/
├── data/
├── image/
└── spectrogram/
```

---

This project provides tools to analyze and optimize Suno AI prompts. Feel free to explore the dataset and contribute improvements to the code!


## Author

**Senthil Nayagam**  
Email: senthil @ muonium.ai
[X ](https://x.com/senthilnayagam)
