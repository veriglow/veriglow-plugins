# CiteAnything Works workflow

Use the first-party `citeanything` CLI for local Work lifecycle operations. SyncAnything may index Works but is not allowed to authoritatively create or update them.

First run `citeanything --help`. If the command is unavailable, stop and ask the user to install the official CiteAnything CLI; do not bypass the missing client with an improvised raw Works API upload.

## Authentication

Generate a dedicated **CLI / TUI** key from the CiteAnything account sidebar, then connect it through the hidden prompt:

```bash
citeanything auth connect --site international
citeanything auth status
```

Use `--site china` for `https://citeanything.cn`. Native `auth connect` currently stores metadata in `~/.citeanything/connections.json` and its secret in macOS Keychain. On other platforms, or for non-interactive automation, inject `CITEANYTHING_CLI_API_KEY` through the secure runtime and optionally set `CITEANYTHING_BASE_URL`.

Do not reuse `CITEANYTHING_API_KEY` or a SyncAnything key.

## Create a Work

1. Make one clean directory named for the deliverable.
2. Generate editable source plus final rendered output.
3. Add `citations.json` with stable number, full token, citation URL, claim, and source URL for each citation.
4. Add a concise `README.md` describing entrypoints and how the result was generated.
5. Render and inspect every final format.
6. Create the remote Work:

```bash
citeanything works create ./my-work --name my-work --connection international
```

The remote path is `outputs/my-work`. Creation refuses an existing path.

## Update a Work

```bash
citeanything works list --connection international
citeanything works pull outputs/my-work ./my-work --connection international
# Edit and validate files.
citeanything works push ./my-work
```

Always pull before editing an existing remote Work. The local `.citeanything-work.json` records the account, Work path, and base revision. The CLI excludes it and `.git` from uploads.

If push returns a conflict, stop. Preserve local edits separately, pull the newest remote revision into a new directory, reconcile deliberately, and push from that new checkout. Never alter the saved revision to force an overwrite.

## Packaging by format

- HTML: include an `index.html`; keep it self-contained where practical. Public preview runs in a script-disabled sandbox, so essential content must not depend on JavaScript.
- PPTX: include the `.pptx`, editable source, and a companion PDF for preview.
- PDF: include the PDF and the source used to create it.
- Markdown or documents: include source plus any useful exported preview.
- Multi-file project: keep all runtime assets inside the Work directory and use relative paths.

Do not include caches, virtual environments, package-manager stores, credentials, `.env` files, browser profiles, or unrelated workspace data.

## Citation rendering contract

Conversation syntax and Work presentation are different:

- Conversation: `[@ev:TOKEN]`.
- Visible Work: green rounded numeric badge with white text and an external link to the citation URL.
- Metadata: full token retained in `citations.json`.

For PPTX, put the hyperlink on the visible badge. Convert to PDF and inspect the PDF's link annotations, not only its appearance. For HTML, use a normal `<a href="..." target="_blank" rel="noopener noreferrer">` badge.

Before syncing, search visible source for `[@ev:` and known token strings. They may exist in `citations.json`, but never as visible artifact text.

## Validation checklist

- Open the intended entrypoint and inspect layout.
- Render every slide/page and check clipping, missing fonts, and broken assets.
- Click citation badges in HTML/PPTX where possible.
- Confirm PDF contains link annotations for its badges.
- Confirm each number maps to exactly one `citations.json` record.
- Confirm the directory contains no secret or unrelated file.
- Use `citeanything works create` once; use `citeanything works push` for later revisions.
