from pathlib import Path

import json
import shutil

def purge_directory(path: str):
    """
    Removes the directory at 'path' (if it exists) and recreates it as empty.
    """
    p = Path(path)
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True, exist_ok=True)

def file_exists(path: str):
    p = Path(path)
    return p.exists()

def get_json(path: str):
    p = Path(path)

    if p.exists():
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
        
    return None