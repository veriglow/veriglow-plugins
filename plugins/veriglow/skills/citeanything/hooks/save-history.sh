#!/bin/bash
# CiteAnything — Stop hook: save Q&A + citations after each response
#
# Reads Claude Code transcript, extracts latest user question + Claude answer,
# and any citeanything.veri-glow.com/e/* URLs, then saves to
# ~/.citeanything/history/{timestamp}.md

set -e

# Bug #1: Detect a working Python interpreter.
# On Windows, `python3` is a Microsoft Store launcher stub that exits non-zero.
if python3 -c "" >/dev/null 2>&1; then
  PYTHON=python3
elif python -c "" >/dev/null 2>&1; then
  PYTHON=python
else
  exit 0
fi

INPUT=$(cat)
TRANSCRIPT_PATH=$("$PYTHON" -c "import sys, json; print(json.load(sys.stdin).get('transcript_path', ''))" <<<"$INPUT" 2>/dev/null || echo "")

if [ -z "$TRANSCRIPT_PATH" ] || [ ! -f "$TRANSCRIPT_PATH" ]; then
  exit 0
fi

# Allow user to override save location via env var.
# Default: ~/.citeanything/history
HISTORY_DIR="${CITEANYTHING_HISTORY_DIR:-$HOME/.citeanything/history}"
mkdir -p "$HISTORY_DIR"

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
OUTFILE="$HISTORY_DIR/${TIMESTAMP}.md"

# Bug #3: Git Bash /c/... paths can't be opened by Python on Windows.
# cygpath -m gives mixed mode (forward slashes, Windows drive letter).
if command -v cygpath >/dev/null 2>&1; then
  TRANSCRIPT_PATH=$(cygpath -m "$TRANSCRIPT_PATH")
  OUTFILE=$(cygpath -m "$OUTFILE")
fi

# Bug #4: Pass paths via env vars instead of heredoc substitution, to avoid
# string-interpolation hazards with backslashes, non-ASCII, quotes, etc.
export TRANSCRIPT_PATH OUTFILE

"$PYTHON" <<'PYEOF'
import json
import os
import re
import sys

transcript_path = os.environ["TRANSCRIPT_PATH"]
outfile = os.environ["OUTFILE"]

user_msg = ""
assistant_msg = ""

def extract_text(content):
    """Content may be a string or a list of blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(parts)
    return ""

try:
    # Bug #5: Explicit UTF-8 encoding. Windows Python defaults to the system
    # locale encoding (cp936/cp1252) which fails on UTF-8 transcripts.
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Bug #2 (critical): Claude Code transcript stores role + content
            # nested under entry["message"], not at the top level. Top-level
            # has only "type". Without this fix, content is always empty and
            # the hook silently exits on every platform.
            entry_type = entry.get("type")
            message = entry.get("message") if isinstance(entry.get("message"), dict) else {}
            role = message.get("role") or entry.get("role") or entry_type
            content = extract_text(message.get("content") or entry.get("content", ""))

            if role == "user" and content:
                user_msg = content
            elif role == "assistant" and content:
                assistant_msg = content
except Exception:
    sys.exit(0)

if not assistant_msg:
    sys.exit(0)

urls = re.findall(r"https://citeanything\.veri-glow\.com/e/[A-Za-z0-9_-]+", assistant_msg)
unique_urls = list(dict.fromkeys(urls))

if not unique_urls:
    sys.exit(0)

with open(outfile, "w", encoding="utf-8") as f:
    f.write("# Question\n\n")
    f.write(user_msg.strip() + "\n\n")
    f.write("# Answer\n\n")
    f.write(assistant_msg.strip() + "\n\n")
    f.write("# Citations\n\n")
    for i, url in enumerate(unique_urls, 1):
        f.write(f"- [{i}] {url}\n")

print(f"Saved: {outfile}")
PYEOF

exit 0
