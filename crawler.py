import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from downloader import download_page, get_html
from utils import get_local_page_folder_name 

def crawl_domain(start_url, snapshot_root, use_selenium=True):

    visited = set() 
    to_visit = [start_url] 
    base_netloc = urlparse(start_url).netloc 

    while to_visit:
        url = to_visit.pop(0) 
        
        if url.endswith('/'):
            normalized_url = url
        else:
            normalized_url = url + '/'
            
        if normalized_url in visited:
            continue
        visited.add(normalized_url)

        print(f"[crawl] Procesez: {url}")
        
        page_folder_name = get_local_page_folder_name(url)
        output_dir_for_page = os.path.join(snapshot_root, page_folder_name)
        
        try:

            download_page(url, output_dir_for_page, snapshot_root, use_selenium=use_selenium)
        except Exception as e:
            print(f"[eroare] Nu am putut descărca {url} — {e}")
            continue

        try:

            html = get_html(url, use_selenium)
            if not html:
                print(f"[skip-links] Nu am putut obține HTML pentru {url}")
                continue
            
            soup = BeautifulSoup(html, 'html.parser')
            
            for a in soup.find_all('a', href=True):
                link = urljoin(url, a['href']) 
                parsed_link = urlparse(link)
                
                # Verifică dacă link-ul este intern (același domeniu) și nu este un fragment (#)
                if parsed_link.netloc == base_netloc and parsed_link.fragment == '':

                    if link.endswith('/'):
                        normalized_link = link
                    else:
                        normalized_link = link + '/'
                        
                    if normalized_link not in visited:
                        to_visit.append(link)
        except Exception as e:
            print(f"[skip-link-extraction] Eroare la extragerea link-urilor din {url} — {e}")

