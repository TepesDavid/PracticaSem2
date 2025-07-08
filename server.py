from flask import Flask, request, send_file
import os

app = Flask(__name__)
ARCHIVE_DIR = "archive"

@app.route("/")
def index():
    """Afișează lista site-urilor arhivate"""
    if not os.path.exists(ARCHIVE_DIR):
        return "<h1>⚠️ Nicio arhivă disponibilă.</h1>"

    sites = sorted(os.listdir(ARCHIVE_DIR))
    links = [f"<li><a href='/site/{site}'>{site}</a></li>" for site in sites]
    return f"<h1>🌐 Arhive disponibile</h1><ul>{''.join(links)}</ul>"

@app.route("/site/<site>")
def list_snapshots(site):
    """Afișează lista versiunilor (snapshot-urilor) pentru un site"""
    site_dir = os.path.join(ARCHIVE_DIR, site)
    if not os.path.exists(site_dir):
        return f"<h2>Nu există arhivă pentru {site}</h2>"

    snapshots = sorted(os.listdir(site_dir))
    if not snapshots:
        return f"<p>Nu există snapshot-uri salvate pentru {site}</p>"

    links = [f"<li><a href='/snapshot/{site}/{snap}'>{snap}</a></li>" for snap in snapshots]
    return f"<h2>🕒 Versiuni arhivate pentru <code>{site}</code></h2><ul>{''.join(links)}</ul>"

@app.route("/snapshot/<site>/<version>")
def list_pages_in_snapshot(site, version):
    """Afișează lista paginilor HTML pentru un snapshot"""
    base = os.path.join(ARCHIVE_DIR, site, version)
    if not os.path.exists(base):
        return f"<h2>Snapshot-ul {version} nu există pentru {site}</h2>"

    pages = []
    for root, dirs, files in os.walk(base):
        for file in files:
            if file.endswith(".html"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base)
                pages.append(rel_path.replace("\\", "/"))

    if not pages:
        return f"<p>Nu există pagini HTML salvate în {version}</p>"

    links = [f"<li><a href='/view/{site}/{version}/{page}'>{page}</a></li>" for page in sorted(pages)]
    return f"<h2>📄 Pagini din snapshot <code>{version}</code> pentru <code>{site}</code></h2><ul>{''.join(links)}</ul>"

@app.route("/view/<site>/<version>/<path:page>")
def view_snapshot_page(site, version, page):
    """Servește un fișier HTML dintr-un snapshot"""
    page_path = os.path.join(ARCHIVE_DIR, site, version, page)
    if os.path.exists(page_path):
        return send_file(page_path)
    return f"<h1>404</h1><p>Pagina nu a fost găsită: {page}</p>"

if __name__ == "__main__":
    app.run(debug=True)
