from flask import Flask, request, send_file, render_template_string, abort
import os
import mimetypes 

app = Flask(__name__)
ARCHIVE_DIR = "archive"

mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("image/jpeg", ".jpeg")
mimetypes.add_type("image/png", ".png")
mimetypes.add_type("image/gif", ".gif")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("font/woff", ".woff")
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("font/ttf", ".ttf")
mimetypes.add_type("font/otf", ".otf")


TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Internet Archive Viewer</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .container { max-width: 960px; }
        .list-group-item a { text-decoration: none; color: #007bff; }
        .list-group-item a:hover { text-decoration: underline; }
        .btn-back { margin-top: 20px; }
    </style>
</head>
<body class="bg-light">
<div class="container py-4 rounded-lg shadow-lg bg-white mt-5 p-4">
    <h1 class="mb-4 text-center text-primary">{{ title }}</h1>
    {% if items %}
        <ul class="list-group list-group-flush">
            {% for label, link in items %}
            <li class="list-group-item d-flex justify-content-between align-items-center rounded-lg mb-2 shadow-sm">
                <a href="{{ link }}" class="flex-grow-1 p-2">{{ label }}</a>
                <span class="badge bg-primary rounded-pill">{{ loop.index }}</span>
            </li>
            {% endfor %}
        </ul>
    {% else %}
        <p class="text-muted text-center">Nu există rezultate.</p>
    {% endif %}
    {% if back_link %}
        <div class="text-center">
            <a href="{{ back_link }}" class="btn btn-secondary btn-back rounded-pill shadow">Înapoi</a>
        </div>
    {% endif %}
</div>
</body>
</html>
"""

@app.route("/")
def index():

    if not os.path.exists(ARCHIVE_DIR):
        return render_template_string(TEMPLATE, title="⚠️ Nicio arhivă disponibilă.", items=[], back_link=None)
    
    sites = sorted(os.listdir(ARCHIVE_DIR))
    items = [(site, f"/site/{site}") for site in sites]
    return render_template_string(TEMPLATE, title="🌐 Arhive disponibile", items=items, back_link=None)

@app.route("/site/<site>")
def list_snapshots(site):
    
    site_dir = os.path.join(ARCHIVE_DIR, site)
    if not os.path.exists(site_dir):
        abort(404, description=f"Arhiva pentru domeniul '{site}' nu a fost găsită.")
        
    snapshots = sorted(os.listdir(site_dir), reverse=True) 
    items = [(snap, f"/snapshot/{site}/{snap}") for snap in snapshots]
    return render_template_string(TEMPLATE, title=f"Snapshot-uri pentru {site}", items=items, back_link="/")

@app.route("/snapshot/<site>/<version>")
def list_pages_in_snapshot(site, version):

    base_snapshot_path = os.path.join(ARCHIVE_DIR, site, version)
    if not os.path.exists(base_snapshot_path):
        abort(404, description=f"Snapshot-ul '{version}' pentru '{site}' nu a fost găsit.")
    
    pages = []

    for item_name in os.listdir(base_snapshot_path):
        item_path = os.path.join(base_snapshot_path, item_name)
        
        if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, 'index.html')):
           
            pages.append(item_name) 
            
    items = []
    for page_folder_name in sorted(pages):
        
        view_link = f"/view/{site}/{version}/{page_folder_name}/index.html"
        
        items.append((page_folder_name, view_link))

    return render_template_string(TEMPLATE, title=f"Pagini salvate în {version}", items=items, back_link=f"/site/{site}")

@app.route("/view/<site>/<version>/<path:page_path>")
def view_snapshot_page(site, version, page_path):

    full_file_path = os.path.join(ARCHIVE_DIR, site, version, page_path)

    
    if not os.path.exists(full_file_path) or \
       not os.path.abspath(full_file_path).startswith(os.path.abspath(os.path.join(ARCHIVE_DIR, site, version))):
        abort(404, description=f"Fișierul nu a fost găsit sau acces interzis: {page_path}")


    mime_type, _ = mimetypes.guess_type(full_file_path)
    if mime_type is None:
        mime_type = 'application/octet-stream' 

    return send_file(full_file_path, mimetype=mime_type)

if __name__ == "__main__":
    import sys
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    
    print("\n[i] Serverul web pornește...")
    print("[i] Accesează http://127.0.0.1:5000 în browser.")
    app.run(debug=True) 
