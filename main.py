from crawler import crawl_domain
from downloader import download_page
from utils import load_dictionary, get_timestamp_folder
import os

BASE_URL = "https://lauracaltea.ro/despre-mine-cititoarea-de-cursa-lunga"
ARCHIVE_DIR = "archive"

if __name__ == "__main__":
    snapshot_dir = get_timestamp_folder(BASE_URL, ARCHIVE_DIR)
    os.makedirs(snapshot_dir, exist_ok=True)

    print(f"[i] Salvez snapshot în: {snapshot_dir}")
    crawl_domain(BASE_URL, snapshot_dir)

    print("[i] Încerc URL-urile din dicționar...")
    dictionary = load_dictionary("urls_to_try.txt")
    for path in dictionary:
        full_url = BASE_URL.rstrip("/") + path
        download_page(full_url, os.path.join(snapshot_dir, path.strip("/")))

    print("[✓] Snapshot complet salvat.")
