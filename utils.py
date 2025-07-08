import os
from datetime import datetime
from urllib.parse import urlparse

def get_timestamp_folder(base_url, archive_root):
    domain = urlparse(base_url).netloc
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return os.path.join(archive_root, domain, timestamp)
    
def load_dictionary(filename):
    try:
        with open(filename, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"[!] Fișierul {filename} nu există.")
        return []
