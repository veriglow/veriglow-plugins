---
name: citeanything
description: >
  Create verifiable evidence citations for data claims. Use after obtaining data
  from web APIs or KB documents to create citations with source links, text anchors,
  and automatic screenshots. Returns [@ev:TOKEN] markers to embed in responses.
license: MIT
compatibility: Works with Claude Code and compatible AI agents
metadata:
  author: VeriGlow
  version: "0.1.0"
  openclaw:
    emoji: "📎"
    homepage: "https://citeanything.veri-glow.com"
    requires:
      bins:
        - curl
---

# CiteAnything — Verifiable Evidence Citations

CiteAnything creates verifiable, replayable citations for every data claim. Each citation stores the source URL, a text anchor for highlight positioning, and triggers an automatic screenshot as visual proof.

## When to Use This Skill

Use this skill **after** you have obtained data (from a web API, web page, or KB document) and need to:
- Create a verifiable citation linking a claim to its source
- Generate a `[@ev:TOKEN]` marker to embed in your response
- Enable the user to click through and see the original source with the relevant text highlighted

**Every data claim in your response must have a citation.** Never skip the citation step.

## Authentication Setup

CiteAnything API requires an API key. If `$CITEANYTHING_API_KEY` is not set in your environment, read [references/api-key-setup.md](references/api-key-setup.md) and guide the user through the setup steps.

Use the key in API calls as a Bearer token: `Authorization: Bearer $CITEANYTHING_API_KEY`

## API Endpoint

```
POST https://citeanything.veri-glow.com/api/citation
```

**Authentication:** `Authorization: Bearer $CITEANYTHING_API_KEY`

### Important: curl usage notes

1. **Timeout:** The API may trigger screenshot generation and take 30-90 seconds. Always use `--max-time 120` to avoid Cloudflare 524 timeout errors.

2. **Non-ASCII content (Chinese, Japanese, etc.):** Shell argument encoding may corrupt Unicode in `curl -d '...'`. Write the JSON payload to a temp file first, then use `curl -d @file`:

```bash
python3 -c "
import json
payload = {
    'claim': '...', 'source_url': '...', 'quoted_text': '...',
    'anchor': '...', 'citation_type': 'text', 'source_type': 'web'
}
with open('/tmp/citation.json', 'w', encoding='utf-8') as f:
    json.dump(payload, f, ensure_ascii=False)
"
curl -s --max-time 120 -X POST "https://citeanything.veri-glow.com/api/citation" \
  -H "Authorization: Bearer $CITEANYTHING_API_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/citation.json
```

3. **Python HTTP clients:** Python's `urllib` and `requests` may be blocked by Cloudflare (error 1010). Use `curl` via Bash for API calls.

## Request Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `claim` | string | **Yes** | — | The claim being cited (e.g. "Tesla's total revenues were $94.8B") |
| `source_url` | string | **Yes** | — | URL of the data source |
| `quoted_text` | string | No | `""` | Verbatim excerpt (1-3 sentences) from the source. **Must be copied exactly — never paraphrase.** |
| `citation_type` | string | No | `"text"` | `"text"` for text citations, `"table"` for table citations |
| `action_steps` | string | No | `""` | JSON string of browser action steps (for dynamic pages) |
| `anchor` | string | No | `""` | Short verbatim excerpt (5-10 words) for highlight positioning. **Must be exact copy from source.** |
| `row_anchor` | string | No | `""` | Table citation: row identifier |
| `col_anchor` | string | No | `""` | Table citation: column identifier |
| `selection_scope` | string | No | `"cell"` | Table citation: `"cell"` or `"row"` |
| `source_type` | string | No | `"web"` | `"web"` for web sources, `"kb"` for knowledge base documents |
| `kb_file` | string | No | `""` | KB document file stem (e.g. `"bd922df1043e"`) |
| `page` | string | No | `""` | KB document page number for highlight positioning |

## Response

```json
{
  "token": "a1b2c3d4",
  "uid": "unique-id",
  "url": "https://citeanything.veri-glow.com/e/a1b2c3d4"
}
```

## Usage: Embed in Response

Citations follow academic style: both the cited claim/value AND a superscript number are hyperlinked, with a references list at the end.

**Inline format:** `[claim text](url)[[N]](url)` — number in brackets immediately after the linked claim.

**Example:**

```
Tesla's [total revenues in 2025 were $94.8 billion](https://citeanything.veri-glow.com/e/abc123)[[1]](https://citeanything.veri-glow.com/e/abc123), with a [gross margin of 18.2%](https://citeanything.veri-glow.com/e/def456)[[2]](https://citeanything.veri-glow.com/e/def456).

...

## References

[1] [Tesla 2025 Annual Report — Total Revenues](https://citeanything.veri-glow.com/e/abc123)
[2] [Tesla 2025 Annual Report — Gross Margin](https://citeanything.veri-glow.com/e/def456)
```

**Rules:**
- The claim link wraps the **full factual statement** (not just the number) — claims are the unit of citation, not individual data points
- Numbers are sequential ([1], [2], [3]...) in order of first appearance
- The same source reused later keeps the same number
- The bottom **References** section lists each citation with a short descriptive title
- For tables, link the cell value + append the number:
  ```
  | Tesla | [$94.8B](url)[[1]](url) |
  ```

> **Auto-save history**: If the user has configured the Stop hook (see [references/api-key-setup.md](references/api-key-setup.md)), each Q&A + citations is automatically saved to `~/.citeanything/history/`. No manual saving needed.

> **Note for CiteAnything web app**: The app's `CLAUDE.md` overrides this format to use `[@ev:TOKEN]` markers, which the frontend renders as inline citation badges. If you are working inside the CiteAnything workspace and see `[@ev:TOKEN]` instructions in `CLAUDE.md`, follow those instead.

## Example: Web Citation

```bash
curl -s --max-time 120 -X POST "https://citeanything.veri-glow.com/api/citation" \
  -H "Authorization: Bearer $CITEANYTHING_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "Shanghai SSE bond trading volume was 2,087.45 billion RMB",
    "source_url": "https://www.sse.com.cn/market/bonddata/overview/day/",
    "quoted_text": "成交金额(亿元) 2,087.45",
    "citation_type": "text",
    "anchor": "成交金额 2,087.45",
    "source_type": "web",
    "action_steps": "[{\"action\":\"navigate\",\"url\":\"https://www.sse.com.cn/market/bonddata/overview/day/\"}]"
  }'
```

## Example: KB Document Citation

When citing knowledge base documents, use `source_type: "kb"` with additional KB-specific fields:

```bash
curl -s --max-time 120 -X POST "https://citeanything.veri-glow.com/api/citation" \
  -H "Authorization: Bearer $CITEANYTHING_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "Tesla total revenues in 2025 were $94.8 billion",
    "source_url": "https://citeanything.veri-glow.com/kb/user/1/abc123def456.html",
    "quoted_text": "Total revenues 94,827 97,690 96,773 Cost of revenues 76,303 79,087 79,113 Gross profit 18,524 18,603 17,660",
    "anchor": "Total revenues 94,827",
    "citation_type": "text",
    "source_type": "kb",
    "kb_file": "abc123def456",
    "page": "53"
  }'
```

**KB citation rules:**
- `anchor`: short verbatim excerpt (5-10 words) — **exact copy** from extracted text, used for highlight positioning
- `quoted_text`: longer verbatim passage (1-3 sentences) surrounding the anchor — **exact copy**, used for context highlighting. If no longer passage is available, set equal to `anchor`
- `page`: the **actual** page number where the text was extracted — never guess
- Both `anchor` and `quoted_text` must be copied verbatim from your extraction output. Never paraphrase, reorganize, or combine text from different parts of the document

## Text vs Table Citations

### Text citations (`citation_type: "text"`)
Use `anchor` + `quoted_text` for positioning. The replay system highlights the matching text on the source page.

### Table citations (`citation_type: "table"`)
Use `row_anchor` + `col_anchor` for cell-level positioning:
- `row_anchor`: identifies the row (e.g. `"国债"`, `"Tesla Inc"`)
- `col_anchor`: identifies the column header (e.g. `"成交金额"`, `"Revenue"`)
- `selection_scope`: `"cell"` highlights one cell, `"row"` highlights the entire row

## Action Steps (for dynamic pages)

For pages that require user interaction to show specific data (e.g., selecting a date), include `action_steps` as a JSON string in the citation. The screenshot service and replay.js execute these steps before capturing/highlighting.

**Supported step types:**

| type | Fields | Description |
|------|--------|-------------|
| `exec_js` | `code`, `wait` | Execute JavaScript on the page |
| `navigate` | `url` | Navigate to a URL (usually skipped — already on page) |
| `click` | `selector` | Click an element |
| `scroll` | `direction`, `amount` | Scroll the page |
| `wait` | `ms` | Wait for a duration |

**Example** — switch to a specific date on SSE bond page:

```json
[
  {"type": "exec_js", "code": "document.querySelector('.js_date input').value = '2026-04-07'", "wait": 0},
  {"type": "exec_js", "code": "overviewDay.setOverviewDayParams()", "wait": 3000}
]
```

**Important:** Use `type` (not `action`), `code` (not `expression`), `selector` (not `css`). AgentMap's `action_steps_template` field provides the correct format with `{{date}}` placeholders — replace them with actual values.

**Do NOT use** Playwright-style fields like `action: "fill"`, `action: "evaluate"`, `expression: "..."` — these are not recognized.

## Workflow

1. **Get data**:
   - **KB documents** → `curl` + Python extraction
   - **Web/live data** → check AgentMap for API specs, then fetch data:

     **Step 1: Query AgentMap** — strip the protocol from the target URL and prepend `agentmap.veri-glow.com/`:

     ```bash
     # Target: https://www.sse.com.cn/market/bonddata/overview/day/
     # AgentMap query:
     curl -s "https://agentmap.veri-glow.com/www.sse.com.cn/market/bonddata/overview/day"
     ```

     - If it returns JSON with API specs → use the documented endpoint to get data
     - If it returns `map_not_found` → report the missing URL (see below), then try `curl` the page directly or web search as fallback

     **Path format rules:**
     - Use the full domain + path, without `https://`
     - Keep `www.` if the original URL has it
     - Remove trailing slash

2. **Create citation** — `POST /api/citation` for each claim (this skill)
3. **Embed markers** — insert citation links in your response text
4. **Never skip citations** — every data claim needs evidence backing

### Reporting AgentMap issues

Report problems so the data can be improved for future agents:

```bash
curl -s -X POST "https://agentmap.veri-glow.com/api/request-map" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "www.example.com/data-page",
    "type": "missing",
    "user_query": "what the user asked"
  }'
```

**Issue types:** `missing` (URL not indexed), `incomplete` (map exists but parameters/fields missing), `incorrect` (map data is wrong).

**Important:** If you had to reverse-engineer a page (read JS source, guess parameter names) because the agentmap data was insufficient, report it as `incomplete` with a `detail` field describing what was missing:

```bash
curl -s -X POST "https://agentmap.veri-glow.com/api/request-map" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "www.sse.com.cn/market/stockdata/marketvalue/main",
    "type": "incomplete",
    "detail": "Missing params: SEARCH_DATE, LIST_BOARD, NEGO_VALUE_DESC",
    "user_query": "上交所流通市值排名"
  }'
```

This does not block your work — still attempt to get the data by other means after reporting.

## Knowledge Base (KB) — Two Modes

| Mode | When to use | PDF leaves machine? |
|------|-------------|-------------------|
| **Server mode** | Need shareable, verifiable citations | Yes (uploaded to server) |
| **Local mode** | Confidential/sensitive documents | No (stays on localhost) |

Ask the user: **"Should this document be shareable for others to verify, or keep it local for privacy?"**

---

### Server Mode — Upload to CiteAnything

Users can upload local PDF files to the CiteAnything server for citation. The server converts PDFs to browsable HTML using pdf2htmlEX.

### Step 1: Upload the PDF

```bash
curl -X POST "https://citeanything.veri-glow.com/api/kb/upload" \
  -H "Authorization: Bearer $CITEANYTHING_API_KEY" \
  -F "file=@/path/to/document.pdf" \
  -F "display_name=My Research Report"
```

**Response:**
```json
{
  "doc_id": 42,
  "stem": "bd922df1043e",
  "status": "processing",
  "message": "Document uploaded. Converting to HTML..."
}
```

Save the `stem` — you'll need it for citations.

### Step 2: Wait for conversion

PDF → HTML conversion runs in the background. Poll until `status` becomes `"ready"`:

```bash
curl -s "https://citeanything.veri-glow.com/api/kb/documents" \
  -H "Authorization: Bearer $CITEANYTHING_API_KEY"
```

Check the document's `status` field:
- `"processing"` → still converting, wait a few seconds and retry
- `"ready"` → HTML is available at the `url` field
- `"failed"` → conversion failed

### Step 3: Download and extract text

Once ready, the document is available at:
```
https://citeanything.veri-glow.com/kb/user/{user_id}/{stem}.html
```

**Important:** Do NOT use WebFetch — KB HTML files are too large and WebFetch will only return CSS. Always use `curl` + Python:

```bash
curl -s "https://citeanything.veri-glow.com/kb/user/{user_id}/{stem}.html" -o document.html
```

Then extract text **per page** with Python. Read [pdf2htmlex-structure.md](references/pdf2htmlex-structure.md) for the complete HTML structure guide, extraction script, and common pitfalls. Key rules:

- pdf2htmlEX splits each PDF page into a `<div class="pf" data-page-no="N">`
- Extract text **per page div** — do NOT extract the whole file at once (you'll lose page numbers)
- Replace PUA characters (U+E000–U+F8FF) with spaces
- Use extracted text **verbatim** as `anchor` and `quoted_text` — never edit or reformat

### Step 4: Create KB citation

Use `POST /api/citation` with KB-specific fields (see "Example: KB Document Citation" above). The `page` value must match the actual `data-page-no` where you found the text.

### Listing and deleting documents

```bash
# List all documents
curl -s "https://citeanything.veri-glow.com/api/kb/documents" \
  -H "Authorization: Bearer $CITEANYTHING_API_KEY"

# Delete a document
curl -X DELETE "https://citeanything.veri-glow.com/api/kb/documents/{doc_id}" \
  -H "Authorization: Bearer $CITEANYTHING_API_KEY"
```

---

### Local Mode — Privacy Mode (localhost)

For confidential documents. PDFs are converted locally via Docker and served from localhost. Citations reference `http://localhost:8877/...` — only replayable on the user's own machine.

**Requires:** Docker running with `sergiomtzlosa/pdf2htmlex` image.

#### Step 1: Start the local KB server (run in background)

```bash
python3 scripts/local-kb.py serve
```

Output: `{"status": "serving", "port": 8877, ...}`

Run this once per session. The server stays running.

#### Step 2: Add a PDF

```bash
python3 scripts/local-kb.py add /path/to/confidential.pdf --name "Internal Report Q1"
```

Output:
```json
{
  "status": "ready",
  "stem": "a1b2c3d4e5f6",
  "display_name": "Internal Report Q1",
  "page_count": 15,
  "url": "http://localhost:8877/a1b2c3d4e5f6.html"
}
```

#### Step 3: Download and extract text

Same process as server mode — `curl` the localhost URL, extract text with Python, replace PUA characters:

```bash
curl -s "http://localhost:8877/a1b2c3d4e5f6.html" -o document.html
```

Then extract text per page following [pdf2htmlex-structure.md](references/pdf2htmlex-structure.md).

#### Step 4: Create citation with localhost URL

```bash
curl -s --max-time 120 -X POST "https://citeanything.veri-glow.com/api/citation" \
  -H "Authorization: Bearer $CITEANYTHING_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "Revenue grew 15% year-over-year",
    "source_url": "http://localhost:8877/a1b2c3d4e5f6.html",
    "quoted_text": "Total revenue increased by 15% compared to the prior fiscal year",
    "anchor": "revenue increased by 15%",
    "citation_type": "text",
    "source_type": "kb",
    "kb_file": "a1b2c3d4e5f6",
    "page": "8"
  }'
```

**Note:** The citation record is stored on the server, but the `source_url` points to localhost. The server cannot take screenshots of localhost URLs — replay only works on the user's machine while the local server is running.

#### Listing local documents

```bash
python3 scripts/local-kb.py list
```

## Article Publishing

Publish articles with embedded verifiable citations, hosted at `citeanything.veri-glow.com/a/{slug}`.

Articles use `[@ev:TOKEN]` citation markers in the body — the hosted page renders them as interactive green citation badges (hover to preview, click to verify).

### Create an article

```bash
python3 -c "
import json
payload = {
    'title': 'Tesla Q1 2026 Earnings Analysis',
    'body': '''## Revenue Growth

Tesla reported total revenues of \$25.7 billion in Q1 2026[@ev:abc123], representing a 15% year-over-year increase[@ev:def456].

## Gross Margin

The automotive gross margin improved to 19.3%[@ev:ghi789], driven by cost reductions in battery production.
''',
    'summary': 'Analysis of Tesla Q1 2026 earnings with verifiable citations',
    'status': 'published'
}
with open('/tmp/article.json', 'w', encoding='utf-8') as f:
    json.dump(payload, f, ensure_ascii=False)
"
curl -s --max-time 30 -X POST "https://citeanything.veri-glow.com/api/articles" \
  -H "Authorization: Bearer $CITEANYTHING_API_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/article.json
```

**Response:**
```json
{
  "slug": "tesla-q1-2026-earnings-analysis-3kF9xB",
  "uid": "a_xxxx",
  "url": "https://citeanything.veri-glow.com/a/tesla-q1-2026-earnings-analysis-3kF9xB"
}
```

### List my articles

```bash
curl -s "https://citeanything.veri-glow.com/api/articles" \
  -H "Authorization: Bearer $CITEANYTHING_API_KEY"
```

### Get a published article (public, no auth)

```bash
curl -s "https://citeanything.veri-glow.com/api/articles/{slug}"
```

### Update an article

```bash
python3 -c "
import json
payload = {'body': 'Updated body with new data[@ev:newtoken]...', 'summary': 'Updated summary'}
with open('/tmp/article_update.json', 'w', encoding='utf-8') as f:
    json.dump(payload, f, ensure_ascii=False)
"
curl -s --max-time 30 -X PUT "https://citeanything.veri-glow.com/api/articles/{slug}" \
  -H "Authorization: Bearer $CITEANYTHING_API_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/article_update.json
```

### Delete an article

```bash
curl -s -X DELETE "https://citeanything.veri-glow.com/api/articles/{slug}" \
  -H "Authorization: Bearer $CITEANYTHING_API_KEY"
```

### Article fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | string | **Yes** (create) | — | Article title |
| `body` | string | **Yes** (create) | — | Markdown with `[@ev:TOKEN]` citations |
| `summary` | string | No | `""` | Short summary for SEO and social sharing |
| `cover_image` | string | No | `""` | Cover image URL |
| `status` | string | No | `"published"` | `"draft"` or `"published"` |

### Article publishing workflow

1. **Research & collect data** — use AgentMap + curl to fetch data from sources
2. **Create citations** — `POST /api/citation` for each data claim (returns `[@ev:TOKEN]`)
3. **Compose article** — write markdown body embedding `[@ev:TOKEN]` markers at each cited claim
4. **Publish** — `POST /api/articles` with the composed body
5. **Share** — the returned URL is publicly accessible with interactive citation verification

## Notes

- Web citations automatically trigger a screenshot for visual proof
- KB citations skip screenshots (the document is already hosted)
- The `[@ev:TOKEN]` link takes the user to a replay page that re-opens the source and highlights the cited content
- Use `$CITEANYTHING_API_KEY` environment variable for authentication — API keys start with `ca_` and do not expire
