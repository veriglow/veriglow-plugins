#!/usr/bin/env python3
"""
CiteAnything Local KB — Privacy Mode

Convert local PDFs to HTML using pdf2htmlEX (Docker) and serve via localhost.
Citations use localhost URLs — PDFs never leave your machine.

Usage:
    python3 local-kb.py add /path/to/document.pdf          # Convert and add
    python3 local-kb.py add /path/to/doc.pdf --name "My Report"  # With display name
    python3 local-kb.py list                                # List documents
    python3 local-kb.py serve                               # Start HTTP server
    python3 local-kb.py serve --port 8877                   # Custom port

Requires: Docker with sergiomtzlosa/pdf2htmlex image.
"""

import argparse
import hashlib
import http.server
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

# ─── Config ───
LOCAL_KB_DIR = Path.home() / ".citeanything" / "local-kb"
MANIFEST_FILE = LOCAL_KB_DIR / "manifest.json"
DEFAULT_PORT = 8877
DOCKER_IMAGE = "sergiomtzlosa/pdf2htmlex"


def ensure_kb_dir():
    LOCAL_KB_DIR.mkdir(parents=True, exist_ok=True)


def load_manifest() -> list:
    if MANIFEST_FILE.exists():
        return json.loads(MANIFEST_FILE.read_text())
    return []


def save_manifest(manifest: list):
    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))


def generate_stem(pdf_path: str) -> str:
    """Generate a unique 12-char hex stem from file path + timestamp."""
    raw = f"{pdf_path}_{time.time()}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def convert_pdf(pdf_path: Path, stem: str) -> bool:
    """Convert PDF to HTML using pdf2htmlEX Docker container."""
    output_dir = LOCAL_KB_DIR
    output_file = f"{stem}.html"

    # Copy PDF to KB dir so Docker can access it
    tmp_pdf = output_dir / f"{stem}.pdf"
    shutil.copy2(pdf_path, tmp_pdf)

    try:
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "--platform", "linux/amd64",
                "-v", f"{output_dir}:/pdf",
                "-w", "/pdf",
                DOCKER_IMAGE,
                "pdf2htmlEX",
                "--zoom", "1.3",
                f"{stem}.pdf",
                output_file,
            ],
            capture_output=True, text=True, timeout=600,
        )
        # pdf2htmlEX writes progress to stderr even on success
        if result.returncode != 0:
            print(f"Error: pdf2htmlEX failed (exit code {result.returncode}):\n{result.stderr[:500]}", file=sys.stderr)
            return False
        if not (output_dir / output_file).exists():
            print(f"Error: pdf2htmlEX finished but {output_file} was not created.\nstderr: {result.stderr[:500]}", file=sys.stderr)
            return False
        return True
    except FileNotFoundError:
        print("Error: Docker is not installed or not in PATH.", file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("Error: pdf2htmlEX timed out (>5 min).", file=sys.stderr)
        return False


def count_pages(html_path: Path) -> int:
    """Count pages from pdf2htmlEX output (class='pf ' divs)."""
    content = html_path.read_text(encoding="utf-8", errors="ignore")
    return content.count('class="pf ')


def cmd_add(args):
    """Add a PDF to local KB."""
    pdf_path = Path(args.pdf).resolve()
    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    if pdf_path.suffix.lower() != ".pdf":
        print(f"Error: Only PDF files are supported, got: {pdf_path.suffix}", file=sys.stderr)
        sys.exit(1)

    ensure_kb_dir()
    stem = generate_stem(str(pdf_path))
    display_name = args.name or pdf_path.stem

    print(f"Converting: {pdf_path.name} → {stem}.html ...")
    success = convert_pdf(pdf_path, stem)
    if not success:
        print("Conversion failed.", file=sys.stderr)
        sys.exit(1)

    # Inject replay.js directly into the HTML file (same approach as server's kb.py)
    html_file = LOCAL_KB_DIR / f"{stem}.html"
    replay_js = _find_replay_js()
    if replay_js and html_file.exists():
        html = html_file.read_text(encoding="utf-8", errors="ignore")
        script_tag = f"<script>\n{replay_js}\n</script>"
        if "</body>" in html:
            html = html.replace("</body>", f"{script_tag}\n</body>", 1)
        elif "</BODY>" in html:
            html = html.replace("</BODY>", f"{script_tag}\n</BODY>", 1)
        else:
            html += f"\n{script_tag}"
        html_file.write_text(html, encoding="utf-8")

    html_path = LOCAL_KB_DIR / f"{stem}.html"
    page_count = count_pages(html_path)

    # Update manifest
    manifest = load_manifest()
    manifest.append({
        "stem": stem,
        "filename": pdf_path.name,
        "display_name": display_name,
        "page_count": page_count,
        "file_size": pdf_path.stat().st_size,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    })
    save_manifest(manifest)

    url = f"http://localhost:{DEFAULT_PORT}/{stem}.html"
    print(json.dumps({
        "status": "ready",
        "stem": stem,
        "display_name": display_name,
        "page_count": page_count,
        "url": url,
    }, indent=2))


def cmd_list(args):
    """List all local KB documents."""
    ensure_kb_dir()
    manifest = load_manifest()
    if not manifest:
        print(json.dumps({"documents": []}))
        return

    port = args.port if hasattr(args, "port") else DEFAULT_PORT
    docs = []
    for doc in manifest:
        html_exists = (LOCAL_KB_DIR / f"{doc['stem']}.html").exists()
        docs.append({
            **doc,
            "url": f"http://localhost:{port}/{doc['stem']}.html" if html_exists else None,
            "status": "ready" if html_exists else "missing",
        })
    print(json.dumps({"documents": docs}, indent=2, ensure_ascii=False))


def _find_replay_js() -> str:
    """Find replay.js content from known locations."""
    candidates = [
        # Sibling citeanything project
        Path(__file__).resolve().parent.parent.parent / "citeanything" / "replay" / "replay.js",
        # Common install paths
        Path.home() / "citeanything" / "replay" / "replay.js",
        Path("/opt/citeanything/replay/replay.js"),
        # Cached copy in local KB dir
        LOCAL_KB_DIR / ".replay.js",
    ]
    for p in candidates:
        if p.exists():
            return p.read_text(encoding="utf-8")
    return ""



def cmd_serve(args):
    """Start local HTTP server for KB documents, injecting replay.js into HTML."""
    ensure_kb_dir()
    port = args.port

    os.chdir(LOCAL_KB_DIR)

    class CORSHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            super().end_headers()

        def log_message(self, format, *args):
            pass  # Suppress request logs

    server = http.server.HTTPServer(("127.0.0.1", port), CORSHandler)
    print(json.dumps({
        "status": "serving",
        "port": port,
        "url": f"http://localhost:{port}",
        "documents": len(load_manifest()),
    }))
    # Flush so the agent sees the output immediately
    sys.stdout.flush()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


def main():
    parser = argparse.ArgumentParser(description="CiteAnything Local KB — Privacy Mode")
    sub = parser.add_subparsers(dest="command")

    # add
    p_add = sub.add_parser("add", help="Convert a PDF and add to local KB")
    p_add.add_argument("pdf", help="Path to PDF file")
    p_add.add_argument("--name", help="Display name (default: filename without extension)")

    # list
    p_list = sub.add_parser("list", help="List local KB documents")
    p_list.add_argument("--port", type=int, default=DEFAULT_PORT)

    # serve
    p_serve = sub.add_parser("serve", help="Start local HTTP server")
    p_serve.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port (default: {DEFAULT_PORT})")

    args = parser.parse_args()
    if args.command == "add":
        cmd_add(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "serve":
        cmd_serve(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
