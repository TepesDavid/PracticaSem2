import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions 
from selenium.webdriver.firefox.service import Service as FirefoxService 
import hashlib 
from utils import get_local_page_folder_name, get_local_page_path 

GECKO_DRIVER_PATH = "/usr/local/bin/geckodriver" 

def get_html(url, use_selenium=True):

    if not use_selenium:

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/126.0', 
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5,ro;q=0.3', 
            'DNT': '1', 
            'Upgrade-Insecure-Requests': '1'
        }
        try:
            response = requests.get(url, timeout=15, headers=headers) 
            response.raise_for_status() 
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"[eroare-requests] Nu am putut descărca {url}: {e}")
            return None

    # Selenium configuration for Firefox
    options = FirefoxOptions() 
    options.headless = True # Run browser in invisible mode
    options.add_argument("--window-size=1920,1080") 

    driver = None
    try:
        service = FirefoxService(executable_path=GECKO_DRIVER_PATH) 
        driver = webdriver.Firefox(service=service, options=options) 
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
    
    # Directory for this page's resources
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

    # --- 1. Download and modify paths for resources (img, script, link) ---
    for tag in soup.find_all(['img', 'script', 'link']):
        attr = 'src' if tag.name != 'link' else 'href'
        if tag.has_attr(attr):
            resource_url = urljoin(url, tag[attr]) # Transform to absolute URL
            parsed_resource_url = urlparse(resource_url)

            file_extension = os.path.splitext(parsed_resource_url.path)[1].lower()
            
            if parsed_resource_url.scheme in ['http', 'https'] and parsed_resource_url.netloc and \
               (parsed_resource_url.path != '/' or parsed_resource_url.query or file_extension):
                
                # If no extension, try to guess or use a fallback
                if not file_extension:
                    if tag.name == 'script': file_extension = '.js'
                    elif tag.name == 'link' and tag.has_attr('rel') and 'stylesheet' in tag['rel']: file_extension = '.css'
                    elif tag.name == 'img': file_extension = '.png' 
                    else: file_extension = '.bin' 

                # Use a hash of the full URL for uniqueness
                unique_filename = hashlib.md5(resource_url.encode('utf-8')).hexdigest() + file_extension
                local_resource_path = os.path.join(resources_dir, unique_filename)
                
                try:
                    # Download the resource
                    r = requests.get(resource_url, timeout=10, stream=True)
                    r.raise_for_status()
                    with open(local_resource_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # Modify the HTML attribute to point to the local resource
                    # The path is relative to the current page's directory
                    tag[attr] = os.path.join("_resources", unique_filename).replace(os.sep, '/') 

                except requests.exceptions.RequestException as e:
                    print(f"[skip-resursă] Could not download {resource_url}: {e}")
                    pass 
                except Exception as e:
                    print(f"[skip-resursă] General error downloading {resource_url}: {e}")
                    pass
            else:
                print(f"[DEBUG-RESOURCE] Resource ignored (not a specific file or has empty path): {resource_url}")


    # --- 2. Modify internal links (<a> tags) ---
    for a_tag in soup.find_all('a', href=True):
        original_href = a_tag['href']
        full_link_url = urljoin(url, original_href) 
        parsed_link = urlparse(full_link_url)

        if parsed_link.netloc == base_netloc and not parsed_link.fragment:
            path_extension = os.path.splitext(parsed_link.path)[1].lower()
            
            if path_extension in DOWNLOADABLE_FILE_EXTENSIONS:
                
                print(f"[DEBUG-LINK] Link to downloadable file: {original_href}")
                
                
                unique_filename = hashlib.md5(full_link_url.encode('utf-8')).hexdigest() + path_extension
                local_file_path = os.path.join(resources_dir, unique_filename)
                
                try:
                    r = requests.get(full_link_url, timeout=10, stream=True)
                    r.raise_for_status()
                    with open(local_file_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    

                    a_tag['href'] = os.path.join("_resources", unique_filename).replace(os.sep, '/')
                    print(f"[DEBUG-LINK] Rewrote file link: {original_href} -> {a_tag['href']}")
                except requests.exceptions.RequestException as e:
                    print(f"[skip-fisier] Could not download file {full_link_url}: {e}")
                    pass 
                except Exception as e:
                    print(f"[skip-fisier] General error downloading file {full_link_url}: {e}")
                    pass
            else:
                # This link is to another internal HTML page
                print(f"[DEBUG-LINK] Link to another HTML page: {original_href}")
                
                parts = snapshot_root.split(os.sep)
                site_name = parts[-2]
                version_name = parts[-1]

                # Get the folder name for the target page
                target_page_folder_name = get_local_page_folder_name(full_link_url)

                flask_absolute_url = f"/view/{site_name}/{version_name}/{target_page_folder_name}/index.html"
                
                # Replace the original link with the Flask-friendly absolute URL
                a_tag['href'] = flask_absolute_url
                print(f"[DEBUG-LINK] Rewrote page link: {original_href} -> {a_tag['href']}")
        elif parsed_link.netloc != base_netloc:
            print(f"[DEBUG-LINK] External link left unchanged: {original_href}")
            pass 

    # Save the modified HTML of the page
    page_filename = os.path.join(output_dir, 'index.html')
    try:
        with open(page_filename, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"[✓] Page saved: {page_filename}")
    except Exception as e:
        print(f"[eroare] Could not save page {url} to {page_filename}: {e}")
