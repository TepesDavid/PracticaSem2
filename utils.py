from datetime import datetime
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import os
import re

def get_timestamp_folder(base_url, archive_root):

    domain = urlparse(base_url).netloc
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return os.path.join(archive_root, domain, timestamp)

def load_dictionary(filename):

    try:
        with open(filename, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"[!] Fișierul {filename} nu există. Creați-l cu căi (ex: /about, /contact).")
        return []

def get_local_page_folder_name(url):

    parsed_url = urlparse(url)

    path_and_query = parsed_url.path
    if parsed_url.query:
        path_and_query += '?' + parsed_url.query


    safe_name = re.sub(r'[^\w\-_.]', '_', path_and_query).strip('_')

    if not safe_name:
        return "index"
    
    # Limitează lungimea numelui pentru a evita probleme cu sistemele de fișiere
    max_len = 100
    if len(safe_name) > max_len:
        # Folosește un hash pentru a scurta și asigura unicitatea dacă numele e prea lung
        hash_suffix = hashlib.md5(safe_name.encode('utf-8')).hexdigest()[:8]
        safe_name = safe_name[:max_len - len(hash_suffix) - 1] + '_' + hash_suffix

    return safe_name

def get_local_page_path(url, snapshot_root):

    folder_name = get_local_page_folder_name(url)
    return os.path.join(snapshot_root, folder_name, 'index.html')

