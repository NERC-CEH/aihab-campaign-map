"""
Download habitat JSON files from the Hugging Face bucket into the data/ directory.

Usage:
    python download_data.py

Requires a Hugging Face token with read access to the bucket.
Set the HF_TOKEN environment variable or log in with `huggingface-cli login`.
"""

import os
from pathlib import Path

from huggingface_hub import sync_bucket

BUCKET_ID = "aihab-uk/habitatimages"
LOCAL_DATA_DIR = Path(__file__).parent / "data"

def main():
    LOCAL_DATA_DIR.mkdir(exist_ok=True)
    print(f"Syncing {BUCKET_ID}/metadata -> {LOCAL_DATA_DIR}")
    sync_bucket(
        f"hf://buckets/{BUCKET_ID}/metadata",
        str(LOCAL_DATA_DIR),
        include=["*.json"],
    )
    json_files = list(LOCAL_DATA_DIR.glob("*.json"))
    print(f"Done. {len(json_files)} JSON file(s) in data/")

if __name__ == "__main__":
    main()
