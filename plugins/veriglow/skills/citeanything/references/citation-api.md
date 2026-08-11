# Citation API reference

Use this reference when a citation needs fields beyond the core text example.

## Request fields

| Field | Required | Meaning |
|---|---|---|
| `claim` | yes | The factual statement supported by this citation |
| `source_url` | web only | Original inspected HTTP(S) source |
| `quoted_text` | text citations | Exact surrounding evidence, normally one to three sentences |
| `anchor` | text citations | Short exact substring used for positioning |
| `citation_type` | no | `text` (default) or `table` |
| `row_anchor` | table citations | Exact row identifier |
| `col_anchor` | table citations | Exact real header cell |
| `cell_anchor` | label/value tables | Exact target value cell; requires `row_anchor` |
| `selection_scope` | no | `cell` (default) or `row` |
| `action_steps` | dynamic pages | JSON action array; direct API payloads encode it as a JSON string |
| `source_type` | no | `web` (default) or `kb` |
| `kb_file` | KB only | Owned ready document's `stem` |
| `page` | KB only | Actual page containing the evidence |
| `prefix`, `suffix` | optional | Exact context used to disambiguate repeated text |

Search snippets are never valid `quoted_text`, anchors, or table cells.

## Table examples

Use a real row and column header:

```json
{
  "claim": "Government bond turnover was 2,087.45 billion RMB.",
  "source_url": "https://www.sse.com.cn/market/bonddata/overview/day/",
  "citation_type": "table",
  "source_type": "web",
  "row_anchor": "国债",
  "col_anchor": "成交金额",
  "selection_scope": "cell"
}
```

For a label/value row without a meaningful column header, use `cell_anchor`:

```json
{
  "claim": "Maximum output is 384K.",
  "source_url": "https://example.com/specifications",
  "citation_type": "table",
  "row_anchor": "MAX OUTPUT",
  "cell_anchor": "MAXIMUM: 384K",
  "selection_scope": "cell"
}
```

Never combine adjacent cells into a synthetic anchor.

## Dynamic-page actions

Supported steps:

| `type` | Fields |
|---|---|
| `exec_js` | `code`, optional `wait` |
| `navigate` | `url` |
| `click` | `selector` |
| `scroll` | `direction`, `amount` |
| `wait` | `ms` |

```json
[
  {"type":"exec_js","code":"document.querySelector('.date input').value='2026-04-07'","wait":0},
  {"type":"click","selector":"button.apply"},
  {"type":"wait","ms":3000}
]
```

Use `type`, not `action`; `code`, not `expression`; and `selector`, not `css`.

## Knowledge-base calls

Use the selected base URL and `Authorization: Bearer $CITEANYTHING_API_KEY` for every call.

```text
POST /api/kb/upload
GET  /api/kb/documents
GET  /api/kb/agent/search?query=...&document_id=...&limit=20
GET  /api/kb/agent/page?document_id=...&page=...
DELETE /api/kb/documents/{document_id}
```

The list response returns the owned document `id`, `stem`, readiness, page count, and a short-lived access URL. Do not construct a persistent private KB URL yourself.

For a KB citation, omit `source_url`:

```json
{
  "claim": "Tesla total revenues were $94.8 billion.",
  "quoted_text": "Total revenues 94,827",
  "anchor": "Total revenues 94,827",
  "citation_type": "text",
  "source_type": "kb",
  "kb_file": "abc123def456",
  "page": "53"
}
```

## Manual screenshots

Use `POST /api/citation/manual` only when the user explicitly supplies or approves the screenshot. Prefer automatic screenshot generation for ordinary web citations. Never upload unrelated screen contents or secrets.
