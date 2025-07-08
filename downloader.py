import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def download_page(url, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    for tag in soup.find_all(['img', 'script', 'link']):
        attr = 'src' if tag.name != 'link' else 'href'
        if tag.has_attr(attr):
            resource_url = urljoin(url, tag[attr])
            filename = os.path.basename(urlparse(resource_url).path)
            if not filename: continue
            local_path = os.path.join(output_dir, filename)

            try:
                res = requests.get(resource_url, timeout=5)
                with open(local_path, 'wb') as f:
                    f.write(res.content)
                tag[attr] = filename
            except Exception as e:
                print(f"[skip] {resource_url} — {e}")

    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(str(soup))
