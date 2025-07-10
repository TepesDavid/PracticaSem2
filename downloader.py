import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import hashlib # Pentru a genera nume unice de fișiere
from utils import get_local_page_folder_name, get_local_page_path # Importăm funcțiile helper

CHROME_DRIVER_PATH = "chromedriver" 

def get_html(url, use_selenium=True):

    if not use_selenium:
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,ro;q=0.8', 
            'DNT': '1', # Do Not Track
            'Upgrade-Insecure-Requests': '1'
        }
        try:
            response = requests.get(url, timeout=15, headers=headers) 
            response.raise_for_status() 
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"[eroare-requests] Nu am putut descărca {url}: {e}")
            return None

    # Configurare Selenium
    options = Options()
    options.headless = True # Rulează browser-ul în mod invizibil
    options.add_argument("--no-sandbox") 
    options.add_argument("--disable-dev-shm-usage") # Reduce problemele de memorie
    options.add_argument("--window-size=1920,1080") # Setează o dimensiune a ferestrei pentru a asigura randarea completă

    driver = None
    try:
        driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=options)
        driver.get(url)
        html = driver.page_source
        return html
    except Exception as e:
        print(f"[eroare-selenium] Nu am putut descărca {url} cu Selenium: {e}")
        return None
    finally:
        if driver:
            driver.quit() 

def download_page(url, output_dir, snapshot_root, use_selenium=True):

    os.makedirs(output_dir, exist_ok=True)
    
    resources_dir = os.path.join(output_dir, "_resources")
    os.makedirs(resources_dir, exist_ok=True)

    try:
        html = get_html(url, use_selenium)
        if not html:
            print(f"[skip] Nu am putut obține HTML pentru {url}. Sărit peste descărcare.")
            return
    except Exception as e:
        print(f"[eroare] Nu am putut descărca {url}: {e}")
        return

    soup = BeautifulSoup(html, 'html.parser')
    base_netloc = urlparse(url).netloc 


    DOWNLOADABLE_FILE_EXTENSIONS = [
        '.pdf', '.zip', '.rar', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', 
        '.jpg', '.jpeg', '.png', '.gif', '.svg', '.mp4', '.mp3', '.avi', '.mov', 
        '.txt', '.csv', '.xml', '.json', '.ico', '.webp', '.woff', '.woff2', '.ttf', '.otf'
    ]

    for tag in soup.find_all(['img', 'script', 'link']):
        attr = 'src' if tag.name != 'link' else 'href'
        if tag.has_attr(attr):
            resource_url = urljoin(url, tag[attr]) 
            parsed_resource_url = urlparse(resource_url)

            # Verifică dacă resursa este internă sau externă și dacă este un fișier valid
            if parsed_resource_url.scheme in ['http', 'https'] and parsed_resource_url.netloc:
                file_extension = os.path.splitext(parsed_resource_url.path)[1].lower()
                # Dacă nu are extensie, încercăm să ghicim sau să punem un fallback
                if not file_extension:
                    if tag.name == 'script': file_extension = '.js'
                    elif tag.name == 'link' and tag.has_attr('rel') and 'stylesheet' in tag['rel']: file_extension = '.css'
                    elif tag.name == 'img': file_extension = '.png' # Fallback comun
                    else: file_extension = '.bin' # Fallback generic

                # Folosim un hash al URL-ului complet pentru unicitate
                unique_filename = hashlib.md5(resource_url.encode('utf-8')).hexdigest() + file_extension
                local_resource_path = os.path.join(resources_dir, unique_filename)
                
                try:
                    # Descarcă resursa
                    r = requests.get(resource_url, timeout=10, stream=True)
                    r.raise_for_status()
                    with open(local_resource_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # Modifică atributul din HTML pentru a puncta către resursa locală
                    # Calea este relativă la directorul paginii curente
                    tag[attr] = os.path.join("_resources", unique_filename).replace(os.sep, '/') # Asigură căile cu slash-uri înainte de salvare
                    # print(f"[resursă] Descărcat {resource_url} la {tag[attr]}") # Comentat pentru a reduce output-ul

                except requests.exceptions.RequestException as e:
                    print(f"[skip-resursă] Nu am putut descărca {resource_url}: {e}")
                    pass 
                except Exception as e:
                    print(f"[skip-resursă] Eroare generală la descărcarea {resource_url}: {e}")
                    pass


    # --- 2. Modifică link-urile interne (<a> tags) ---
    for a_tag in soup.find_all('a', href=True):
        original_href = a_tag['href']
        full_link_url = urljoin(url, original_href) # URL absolut al link-ului

        parsed_link = urlparse(full_link_url)

        print(f"[DEBUG-LINK] Procesez link: {original_href}")
        print(f"[DEBUG-LINK] URL absolut: {full_link_url}")
        print(f"[DEBUG-LINK] Domeniu link: {parsed_link.netloc}, Domeniu bază: {base_netloc}")
        print(f"[DEBUG-LINK] Este intern și nu fragment: {parsed_link.netloc == base_netloc and not parsed_link.fragment}")

        # Verifică dacă link-ul este intern și nu este un fragment (#)
        if parsed_link.netloc == base_netloc and not parsed_link.fragment:
            path_extension = os.path.splitext(parsed_link.path)[1].lower()
            
            if path_extension in DOWNLOADABLE_FILE_EXTENSIONS:
                # Acest link este către un fișier descărcabil (ex: PDF)
                print(f"[DEBUG-LINK] Link către fișier descărcabil: {original_href}")
                
                # Descarcă fișierul în directorul _resources al paginii curente
                unique_filename = hashlib.md5(full_link_url.encode('utf-8')).hexdigest() + path_extension
                local_file_path = os.path.join(resources_dir, unique_filename)
                
                try:
                    r = requests.get(full_link_url, timeout=10, stream=True)
                    r.raise_for_status()
                    with open(local_file_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # Rescrie link-ul din HTML pentru a puncta către fișierul local
                    a_tag['href'] = os.path.join("_resources", unique_filename).replace(os.sep, '/')
                    print(f"[DEBUG-LINK] Rescris link fișier: {original_href} -> {a_tag['href']}")
                except requests.exceptions.RequestException as e:
                    print(f"[skip-fisier] Nu am putut descărca fișierul {full_link_url}: {e}")
                    pass # Lăsăm link-ul original dacă nu se poate descărca
                except Exception as e:
                    print(f"[skip-fisier] Eroare generală la descărcarea fișierului {full_link_url}: {e}")
                    pass
            else:
                # Acest link este către o altă pagină HTML internă
                print(f"[DEBUG-LINK] Link către altă pagină HTML: {original_href}")
                
                # Calculează calea locală unde ar trebui să fie salvată pagina țintă (fișierul index.html)
                target_local_page_file_path = get_local_page_path(full_link_url, snapshot_root)
                
                # Calea directorului paginii curente, de unde se calculează calea relativă
                current_page_local_dir = output_dir 
                
                # Calculează calea relativă de la directorul paginii curente la fișierul index.html al paginii țintă
                relative_path = os.path.relpath(target_local_page_file_path, current_page_local_dir)
                
                # Înlocuiește link-ul original cu calea relativă locală
                a_tag['href'] = relative_path.replace(os.sep, '/') # Asigură căile cu slash-uri
                print(f"[DEBUG-LINK] Rescris link pagină: {original_href} -> {a_tag['href']}")
        elif parsed_link.netloc != base_netloc:
            print(f"[DEBUG-LINK] Link extern lăsat neschimbat: {original_href}")
            pass # Lăsăm link-urile externe neschimbate


    # Salvează HTML-ul modificat al paginii
    page_filename = os.path.join(output_dir, 'index.html')
    try:
        with open(page_filename, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"[✓] Pagina salvată: {page_filename}")
    except Exception as e:
        print(f"[eroare] Nu am putut salva pagina {url} la {page_filename}: {e}")

