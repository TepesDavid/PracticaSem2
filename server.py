from flask import Flask, request, send_file, render_template_string, abort, url_for
import os
import mimetypes 
from urllib.parse import urlparse

app = Flask(__name__)
ARCHIVE_DIR = "archive"

# Adăugăm tipuri MIME comune, dacă nu sunt deja înregistrate
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
        /* Sticky Footer CSS */
        html, body {
            height: 100%; /* Asigură că html și body ocupă înălțimea completă */
            margin: 0;
            padding: 0;
        }
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f8f9fa;
            display: flex; /* Activează Flexbox pe body */
            flex-direction: column; /* Aranjează conținutul pe coloană */
            min-height: 100vh; /* Asigură că body ocupă cel puțin înălțimea viewport-ului */
        }
        .main-content {
            flex-grow: 1; /* Permite containerului de conținut să se extindă și să împingă footer-ul */
        }
        /* End Sticky Footer CSS */

        .navbar { background-color: #007bff; }
        .navbar-brand, .nav-link { color: white !important; }
        .navbar-brand:hover, .nav-link:hover { color: #e9ecef !important; }
        .container { max-width: 960px; }
        .list-group-item a { text-decoration: none; color: #007bff; font-weight: 500; }
        .list-group-item a:hover { text-decoration: underline; }
        .btn-back { margin-top: 20px; }
        .card-header { background-color: #e9ecef; border-bottom: 1px solid #dee2e6; }
        .footer { background-color: #343a40; color: white; padding: 20px 0; text-align: center; } /* Fără margin-top aici */
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark shadow-sm">
        <div class="container">
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li class="nav-item">
                        <a class="nav-link active" aria-current="page" href="{{ url_for('index') }}">Acasă</a>
                    </li>
                </ul>
                <form class="d-flex" action="{{ url_for('search_archives') }}" method="get">
                    <input class="form-control me-2 rounded-pill" type="search" placeholder="Căutați arhive..." aria-label="Search" name="query" value="{{ search_query | default('') }}">
                    <button class="btn btn-outline-light rounded-pill" type="submit">Căutare</button>
                </form>
            </div>
        </div>
    </nav>

    <div class="main-content container py-4 mt-5"> {# Adăugat clasa main-content aici #}
        <div class="card shadow-lg rounded-lg">
            <div class="card-header text-center py-3">
                <h1 class="mb-0 text-primary">{{ title }}</h1>
            </div>
            <div class="card-body p-4">
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
                    <div class="text-center mt-4">
                        <a href="{{ back_link }}" class="btn btn-secondary btn-back rounded-pill shadow">Înapoi</a>
                    </div>
                {% endif %}
            </div>
        </div>
    </div>

    <footer class="footer">
        <div class="container">
            <p class="mb-0">&copy; 2025 Internet Archive Viewer. Toate drepturile rezervate.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route("/")
def index():
    """Listează toate domeniile arhivate disponibile."""
    if not os.path.exists(ARCHIVE_DIR):
        return render_template_string(TEMPLATE, title=" Nicio arhivă disponibilă.", items=[], back_link=None)
    
    sites = sorted(os.listdir(ARCHIVE_DIR))
    items = [(site, f"/site/{site}") for site in sites]
    return render_template_string(TEMPLATE, title="🌐 Arhive disponibile", items=items, back_link=None)

@app.route("/site/<site>")
def list_snapshots(site):
    """Listează snapshot-urile (versiunile) pentru un anumit domeniu."""
    site_dir = os.path.join(ARCHIVE_DIR, site)
    if not os.path.exists(site_dir):
        abort(404, description=f"Arhiva pentru domeniul '{site}' nu a fost găsită.")
        
    snapshots = sorted(os.listdir(site_dir), reverse=True) 
    items = [(snap, f"/snapshot/{site}/{snap}") for snap in snapshots]
    return render_template_string(TEMPLATE, title=f"Snapshot-uri pentru {site}", items=items, back_link="/")

@app.route("/snapshot/<site>/<version>")
def list_pages_in_snapshot(site, version):
    """Listează paginile HTML arhivate într-un anumit snapshot."""
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
        # Link-ul real va fi către index.html din acel folder
        view_link = f"/view/{site}/{version}/{page_folder_name}/index.html"
        # Eticheta afișată poate fi numele folderului, care este mai descriptiv
        items.append((page_folder_name, view_link))

    return render_template_string(TEMPLATE, title=f"Pagini salvate în {version}", items=items, back_link=f"/site/{site}")

@app.route("/view/<site>/<version>/<path:page_path>")
def view_snapshot_page(site, version, page_path):
    """Servește fișierul solicitat din arhiva snapshot."""
    print(f"[SERVER-DEBUG] Request received for site: {site}, version: {version}, page_path: {page_path}")
    
    # Construiește calea completă a fișierului pe sistemul de fișiere
    full_file_path = os.path.join(ARCHIVE_DIR, site, version, page_path)
    print(f"[SERVER-DEBUG] Attempting to serve file from absolute path: {full_file_path}")

    snapshot_base_dir = os.path.abspath(os.path.join(ARCHIVE_DIR, site, version))
    requested_abs_path = os.path.abspath(full_file_path)

    if not os.path.exists(full_file_path):
        print(f"[SERVER-DEBUG] File does NOT exist at: {full_file_path}")
        abort(404, description=f"Fișierul nu a fost găsit: {page_path}")
    
    if not requested_abs_path.startswith(snapshot_base_dir):
        print(f"[SERVER-DEBUG] Directory traversal attempt detected. Requested: {requested_abs_path}, Base: {snapshot_base_dir}")
        abort(403, description=f"Acces interzis: {page_path}")

    # Determină tipul MIME al fișierului
    mime_type, _ = mimetypes.guess_type(full_file_path)
    if mime_type is None:
        mime_type = 'application/octet-stream' # Tip generic 
    
    print(f"[SERVER-DEBUG] Serving {full_file_path} with MIME type {mime_type}")
    return send_file(full_file_path, mimetype=mime_type)

@app.route("/search")
def search_archives():
    """Caută prin domeniile, snapshot-urile și paginile arhivate."""
    query = request.args.get('query', '').strip().lower()
    results = []
    
    if not query:
        return render_template_string(TEMPLATE, title="Căutare Arhive", items=[], search_query=query, back_link="/")

    if not os.path.exists(ARCHIVE_DIR):
        return render_template_string(TEMPLATE, title="Căutare Arhive", items=[], search_query=query, back_link="/")

    # Caută în nume de domenii
    for site_name in os.listdir(ARCHIVE_DIR):
        if query in site_name.lower():
            results.append((f"Domeniu: {site_name}", url_for('list_snapshots', site=site_name)))
        
        site_path = os.path.join(ARCHIVE_DIR, site_name)
        if os.path.isdir(site_path):
            # Caută în nume de snapshot-uri
            for snapshot_name in os.listdir(site_path):
                if query in snapshot_name.lower():
                    results.append((f"Snapshot: {site_name} / {snapshot_name}", url_for('list_pages_in_snapshot', site=site_name, version=snapshot_name)))
                
                snapshot_path = os.path.join(site_path, snapshot_name)
                if os.path.isdir(snapshot_path):
                    # Caută în nume de foldere de pagini
                    for page_folder_name in os.listdir(snapshot_path):
                        if query in page_folder_name.lower():
                            # Verifică dacă este un folder de pagină valid (conține index.html)
                            page_index_path = os.path.join(snapshot_path, page_folder_name, 'index.html')
                            if os.path.exists(page_index_path):
                                results.append((f"Pagină: {site_name} / {snapshot_name} / {page_folder_name}", url_for('view_snapshot_page', site=site_name, version=snapshot_name, page_path=f"{page_folder_name}/index.html")))

    # Elimină duplicatele din rezultate 
    unique_results = []
    seen_links = set()
    for label, link in results:
        if link not in seen_links:
            unique_results.append((label, link))
            seen_links.add(link)

    return render_template_string(TEMPLATE, title=f"Rezultate căutare pentru '{query}'", items=unique_results, search_query=query, back_link="/")


if __name__ == "__main__":
    import sys
    
    print("\n[i] Serverul web pornește...")
    print("[i] Accesează http://127.0.0.1:5000 în browser.")
    app.run(debug=True) 
