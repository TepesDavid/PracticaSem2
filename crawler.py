import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from downloader import download_page

def crawl_domain(start_url, output_root):
    visited = set()
    to_visit = [start_url]
    base_netloc = urlparse(start_url).netloc

    while to_visit:
        url = to_visit.pop()
        if url in visited: continue
        visited.add(url)

        print(f"[crawl] {url}")
        local_folder = os.path.join(output_root, urlparse(url).path.strip("/").replace("/", "_") or "index")
        try:
            download_page(url, local_folder)
            html = requests.get(url).text
            soup = BeautifulSoup(html, 'html.parser')
            for a in soup.find_all('a', href=True):
                full_url = urljoin(url, a['href'])
                if urlparse(full_url).netloc == base_netloc:
                    to_visit.append(full_url)
        except Exception as e:
            print(f"[eroare] {url} — {e}")
