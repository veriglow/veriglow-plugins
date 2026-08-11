---
name: citeanything
description: Create replayable CiteAnything evidence citations from inspected web pages or private knowledge-base documents, and build or synchronize durable cited Works such as HTML, PPTX, PDF, Markdown, and source bundles. Use when an agent must substantiate factual claims, emit CiteAnything citation markers or links, turn research into a cited artifact, or move a local Work into the user's CiteAnything account with the first-party CLI.
---

# CiteAnything

Create evidence that a reader can reopen and verify, then preserve finished artifacts as durable CiteAnything Works.

## Keep the product boundaries clear

| Surface | Credential | Use it for |
|---|---|---|
| CiteAnything skill/API | `CITEANYTHING_API_KEY` | Citations, screenshots, and private knowledge-base documents |
| CiteAnything CLI/TUI | Native connection or `CITEANYTHING_CLI_API_KEY` | Conversations, agent runs, and listing, pulling, creating, or updating Works |
| SyncAnything | `SYNCANYTHING_CITEANYTHING_API_KEY` | Rebuildable local search over conversations and, optionally, read-only Work discovery |

Never substitute one credential for another. Never print, commit, or place a key in a Work directory. If setup is missing, read [references/api-key-setup.md](references/api-key-setup.md).

Use `https://citeanything.app` for the international site and `https://citeanything.cn` for the China site. For direct API calls, respect `CITEANYTHING_BASE_URL` when it is set; otherwise default to the international site. Treat `https://citeanything.veri-glow.com` only as a legacy compatibility origin, never as the default for new links.

## Core citation workflow

1. Inspect the original source. Search results and summaries may discover a source but are not evidence.
2. Copy exact rendered evidence. Never invent or paraphrase an anchor.
3. Create citations, preferably in one batch after verifying all evidence.
4. Insert the returned tokens using the output contract below.
5. If creation fails, correct the payload or choose another accessible source; do not silently ship an uncited factual claim.

### Select the right citation shape

- Ordinary prose: `citation_type: "text"`, with an exact `anchor` and a longer exact `quoted_text`.
- Native HTML table or ARIA grid: `citation_type: "table"`, exact `row_anchor`, and `selection_scope: "cell"` or `"row"`.
- Use `col_anchor` only for a real header cell. For label/value layouts, use exact `cell_anchor` with `row_anchor`.
- Dynamic pages: add `action_steps` only when replay must reproduce an interaction. Use the schema in [references/citation-api.md](references/citation-api.md).
- Private KB evidence: use `source_type: "kb"`, `kb_file`, and the actual `page`; omit `source_url`.

### Create citations

Write a UTF-8 JSON payload to a temporary file, then call the batch endpoint. This avoids shell corruption of non-ASCII evidence.

```json
{
  "citations": [
    {
      "claim": "Tesla reported total revenue of $94.8 billion.",
      "source_url": "https://example.com/report",
      "quoted_text": "Total revenue was $94.8 billion for the year.",
      "anchor": "Total revenue was $94.8 billion",
      "citation_type": "text",
      "source_type": "web"
    }
  ]
}
```

```bash
CITEANYTHING_BASE="${CITEANYTHING_BASE_URL:-https://citeanything.app}"
curl --fail-with-body -sS --max-time 120 \
  -X POST "$CITEANYTHING_BASE/api/citation/batch" \
  -H "Authorization: Bearer $CITEANYTHING_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @/path/to/citations.json
```

The response is an array containing `token`, `uid`, `url`, and whether an identical citation was reused. Citation creation is idempotent for equivalent evidence.

Read [references/citation-api.md](references/citation-api.md) when using tables, dynamic pages, manual screenshots, or unfamiliar request fields.

## Render citations for the destination

### CiteAnything conversations

Use the canonical transport marker immediately after the supported claim:

```text
Tesla reported total revenue of $94.8 billion [@ev:a1b2c3d4].
```

CiteAnything Web, desktop, mobile, and TUI render the marker as an interactive citation.

### Ordinary Markdown outside CiteAnything

Raw markers have no renderer. Link the full factual claim to the returned `url`, append a stable numbered link, and add a References section when appropriate.

```markdown
[Tesla reported total revenue of $94.8 billion](https://citeanything.app/e/a1b2c3d4)[[1]](https://citeanything.app/e/a1b2c3d4).
```

### User-facing Works

Never expose raw `[@ev:TOKEN]` markers or bare token strings in visible HTML, PPTX, or PDF content.

- Assign stable citation numbers in first-appearance order.
- Render a small green rounded badge with a white number.
- Link the badge to `https://citeanything.app/e/TOKEN` (or the selected site's returned URL).
- In PPTX, attach an external hyperlink to the badge shape or text.
- After PDF conversion, verify that each badge remains a real link annotation.
- Preserve complete tokens and source URLs in `citations.json` or equivalent Work metadata.
- Render and visually inspect the final artifact before syncing it.

## Knowledge-base workflow

Private KB documents remain account-scoped. Do not guess server filesystem paths or construct `/kb/user/...` URLs.

1. Upload a supported document with `POST /api/kb/upload` when needed.
2. Poll `GET /api/kb/documents` until the document is `ready`.
3. Search exact evidence with `GET /api/kb/agent/search?query=...`.
4. Read the full matching page with `GET /api/kb/agent/page?document_id=...&page=...`.
5. Create a KB citation with the returned `stem`, actual page number, and verbatim page text.

```bash
CITEANYTHING_BASE="${CITEANYTHING_BASE_URL:-https://citeanything.app}"
curl --fail-with-body -sS \
  "$CITEANYTHING_BASE/api/kb/agent/search?query=total%20revenue&limit=20" \
  -H "Authorization: Bearer $CITEANYTHING_API_KEY"
```

For confidential documents that must not leave the machine, ask the user before using local mode. Read [references/pdf2htmlex-structure.md](references/pdf2htmlex-structure.md) and use `scripts/local-kb.py`; local citations are replayable only while the user's localhost server is available.

## Build and synchronize Works

Use the CiteAnything CLI as the authoritative local automation surface. Do not create or update Works through SyncAnything.

```bash
citeanything auth status
citeanything works list --connection international
citeanything works pull outputs/existing-work ./existing-work --connection international

# Edit and validate the existing checkout, then push optimistically.
citeanything works push ./existing-work

# Or create a new directory Work after generating its files.
mkdir new-work
# Generate source, rendered artifacts, citations.json, and README.md in new-work.
citeanything works create ./new-work --name new-work --connection international
```

`works pull` and `works create` write `.citeanything-work.json`. Do not edit, copy, or publish its credential-adjacent connection metadata. A push uses its saved revision and must surface HTTP 409 conflicts instead of overwriting newer cloud-agent work.

Read [references/works.md](references/works.md) before creating or updating a Work. It defines packaging, citation rendering, validation, and conflict handling.

## AgentMap integration

Use AgentMap when it provides a documented data endpoint or browser recipe for the source. Query with the full domain and path, without the protocol or trailing slash:

```bash
curl -sS "https://agentmap.veri-glow.com/www.sse.com.cn/market/bonddata/overview/day"
```

If no map exists, report the gap through AgentMap and continue with another legitimate inspection method. A map helps retrieve data; it does not replace inspecting the original evidence before citation creation.

## Completion checklist

- Every material factual claim has evidence from an inspected source.
- All text and table anchors are exact copies from that source.
- Conversation output uses `[@ev:TOKEN]`; non-CiteAnything Markdown uses clickable links.
- Visible Works use linked numbered badges and contain no raw markers.
- `citations.json` preserves the full token-to-source mapping.
- HTML/PPTX/PDF output was rendered and checked; PDF hyperlinks survived conversion.
- New Works were created with `citeanything works create`; existing Works were updated with `citeanything works push`.
- No API key, JWT, environment dump, or unrelated workspace file entered the Work.
