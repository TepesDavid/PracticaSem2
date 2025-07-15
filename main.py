from crawler import crawl_domain
from downloader import download_page
from utils import load_dictionary, get_timestamp_folder, get_local_page_folder_name
import os

ARCHIVE_DIR = "archive"
USE_SELENIUM = True 

if __name__ == "__main__":
    base_url = input("Introduceți URL-ul de arhivat (ex: https://www.example.com): ").strip()
    
    if not base_url.endswith('/'):
        base_url += '/'

    snapshot_dir = get_timestamp_folder(base_url, ARCHIVE_DIR)
    os.makedirs(snapshot_dir, exist_ok=True)

    print(f"[i] Salvez snapshot în directorul: {snapshot_dir}")

    crawl_domain(base_url, snapshot_dir, use_selenium=USE_SELENIUM)

    print("[i] Încerc URL-urile din dicționar...")
    dictionary = load_dictionary("urls_to_try.txt")
    for path in dictionary:
        if not path.startswith('/'):
            path = '/' + path
            
        full_url = base_url.rstrip("/") + path 
        
        page_folder_name = get_local_page_folder_name(full_url)
        output_path_for_dict_url = os.path.join(snapshot_dir, page_folder_name)
        
        # Descarcă pagina din dicționar. Aceasta va fi salvată în output_path_for_dict_url/index.html
        download_page(full_url, output_path_for_dict_url, snapshot_dir, use_selenium=USE_SELENIUM)

    print("[✓] Snapshot complet salvat.")

