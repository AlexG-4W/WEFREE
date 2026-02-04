import os
import sys
import ssl
import json
import secrets
from pathlib import Path
from datetime import datetime, timedelta
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session, abort, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from OpenSSL import crypto

# --- Configuration & Security ---
APP_NAME = "WEFREE Portable Server"
CONFIG_FILE = "config.json"
STORAGE_DIR = Path(os.getcwd())
CERT_DIR = Path("certs")

app = Flask(__name__)
app.secret_key = secrets.token_hex(24)

# Ensure certs directory exists
if not CERT_DIR.exists():
    CERT_DIR.mkdir()

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "password_hash": generate_password_hash("admin123"),
            "port": 5000,
            "allow_uploads": True
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f, indent=4)
        return default_config
    
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

config = load_config()

def generate_self_signed_cert():
    cert_path = CERT_DIR / "server.crt"
    key_path = CERT_DIR / "server.key"
    
    if cert_path.exists() and key_path.exists():
        return str(cert_path), str(key_path)

    # Generate key
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)

    # Generate cert
    cert = crypto.X509()
    cert.get_subject().C = "US"
    cert.get_subject().ST = "Local"
    cert.get_subject().L = "Local"
    cert.get_subject().O = "WEFREE"
    cert.get_subject().OU = "WEFREE"
    cert.get_subject().CN = "localhost"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha256')

    with open(cert_path, "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open(key_path, "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
        
    return str(cert_path), str(key_path)

# --- Helpers ---
def is_logged_in():
    return session.get("logged_in")

def get_safe_path(p=""):
    requested_path = (STORAGE_DIR / p).resolve()
    if not str(requested_path).startswith(str(STORAGE_DIR)):
        abort(403)
    return requested_path

# --- Routes ---
@app.before_request
def require_login():
    if not is_logged_in() and request.endpoint not in ("login", "static"):
        return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if check_password_hash(config["password_hash"], password):
            session["logged_in"] = True
            return redirect(url_for("index"))
        flash("Invalid password")
    return render_template_string('''
        <!doctype html>
        <html>
        <head>
            <title>WEFREE Login</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { background: #f8f9fa; display: flex; align-items: center; justify-content: center; height: 100vh; }
                .login-card { width: 100%; max-width: 400px; padding: 2rem; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            </style>
        </head>
        <body>
            <div class="login-card">
                <h2 class="text-center mb-4">WEFREE Access</h2>
                {% with messages = get_flashed_messages() %}
                  {% if messages %}
                    {% for message in messages %}
                      <div class="alert alert-danger">{{ message }}</div>
                    {% endfor %}
                  {% endif %}
                {% endwith %}
                <form method="post">
                    <div class="mb-3">
                        <input type="password" name="password" class="form-control" placeholder="Password" required autofocus>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Unlock</button>
                </form>
            </div>
        </body>
        </html>
    ''')

@app.route("/")
@app.route("/browse/<path:subpath>")
def index(subpath=""):
    full_path = get_safe_path(subpath)
    
    if not full_path.is_dir():
        return send_from_directory(full_path.parent, full_path.name)

    items = []
    for entry in os.scandir(full_path):
        rel_path = os.path.relpath(entry.path, STORAGE_DIR)
        items.append({
            "name": entry.name,
            "is_dir": entry.is_dir(),
            "path": rel_path.replace("", "/"),
            "size": f"{os.path.getsize(entry.path) / 1024:.1f} KB" if entry.is_file() else "-",
            "mtime": datetime.fromtimestamp(entry.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
        })
    
    # Sort: directories first, then alphabetical
    items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
    
    parent = None
    if subpath:
        parent = os.path.dirname(subpath.rstrip("/"))
        if parent == "": parent = None

    return render_template_string(INDEX_TEMPLATE, items=items, current_path=subpath, parent=parent)

@app.route("/upload", methods=["POST"])
def upload():
    if not config.get("allow_uploads"):
        abort(403)
        
    subpath = request.form.get("path", "")
    full_path = get_safe_path(subpath)
    
    if "file" not in request.files:
        return redirect(request.referrer or url_for("index", subpath=subpath))
    
    file = request.files["file"]
    if file.filename == "":
        return redirect(request.referrer or url_for("index", subpath=subpath))
    
    filename = secure_filename(file.filename)
    file.save(full_path / filename)
    return redirect(request.referrer or url_for("index", subpath=subpath))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

def render_template_string(template, **kwargs):
    from flask import render_template_string as flask_render
    return flask_render(template, **kwargs)

INDEX_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>WEFREE - {{ current_path or 'Root' }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <style>
        .breadcrumb-item + .breadcrumb-item::before { content: "/"; }
        .table tr { vertical-align: middle; }
        .icon-dir { color: #ffca28; }
        .icon-file { color: #6c757d; }
    </style>
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-dark mb-4">
        <div class="container">
            <span class="navbar-brand mb-0 h1">WEFREE Portable Server</span>
            <div class="d-flex">
                <a href="{{ url_for('logout') }}" class="btn btn-outline-light btn-sm">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container bg-white p-4 rounded shadow-sm">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb mb-0">
                    <li class="breadcrumb-item"><a href="{{ url_for('index') }}">Root</a></li>
                    {% if current_path %}
                        {% set parts = current_path.split('/') %}
                        {% for part in parts %}
                            <li class="breadcrumb-item active">{{ part }}</li>
                        {% endfor %}
                    {% endif %}
                </ol>
            </nav>
            
            <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#uploadModal">
                <i class="bi bi-upload"></i> Upload
            </button>
        </div>

        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Size</th>
                        <th>Modified</th>
                        <th class="text-end">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% if parent is not none or current_path %}
                        <tr>
                            <td colspan="4">
                                <i class="bi bi-arrow-up-circle"></i>
                                <a href="{{ url_for('index', subpath=parent) if parent else url_for('index') }}" class="text-decoration-none">..</a>
                            </td>
                        </tr>
                    {% endif %}
                    {% for item in items %}
                    <tr>
                        <td>
                            {% if item.is_dir %}
                                <i class="bi bi-folder-fill icon-dir me-2"></i>
                                <a href="{{ url_for('index', subpath=item.path) }}" class="text-decoration-none">{{ item.name }}</a>
                            {% else %}
                                <i class="bi bi-file-earmark-text icon-file me-2"></i>
                                <a href="{{ url_for('index', subpath=item.path) }}" class="text-decoration-none" target="_blank">{{ item.name }}</a>
                            {% endif %}
                        </td>
                        <td class="text-muted small">{{ item.size }}</td>
                        <td class="text-muted small">{{ item.mtime }}</td>
                        <td class="text-end">
                            <a href="{{ url_for('index', subpath=item.path) }}" class="btn btn-sm btn-outline-secondary" {% if not item.is_dir %}download{% endif %}>
                                <i class="bi bi-download"></i>
                            </a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Upload Modal -->
    <div class="modal fade" id="uploadModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <form action="{{ url_for('upload') }}" method="post" enctype="multipart/form-data">
                    <div class="modal-header">
                        <h5 class="modal-title">Upload File</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <input type="hidden" name="path" value="{{ current_path }}">
                        <input type="file" name="file" class="form-control" required>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="submit" class="btn btn-primary">Upload</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

if __name__ == "__main__":
    cert, key = generate_self_signed_cert()
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert, key)
    
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print(f"--- {APP_NAME} ---")
    print(f"Локальный доступ: https://localhost:{config['port']}")
    print(f"Сетевой доступ:  https://{local_ip}:{config['port']}")
    print(f"Папка с файлами: {STORAGE_DIR}")
    print("-------------------------")
    print("ВАЖНО: При входе в браузере подтвердите исключение безопасности (самоподписанный сертификат).")
    
    app.run(host='0.0.0.0', port=config['port'], ssl_context=context, debug=False)
