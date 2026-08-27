<p align="center">
  <img src="https://brand.veri-glow.com/favicon.svg" width="80" alt="VeriGlow Logo" />
</p>

<h1 align="center">CiteAnything</h1>

<p align="center">
  <strong>Verifiable evidence and durable cited Works for AI agents</strong><br>
  Every claim backed by a source. Every artifact owned by the user.
</p>

<p align="center">
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/Agent_Skills-compatible-10B981?style=flat-square" alt="Agent Skills compatible" /></a>
  <a href="https://citeanything.app"><img src="https://img.shields.io/badge/app-citeanything.app-10B981?style=flat-square" alt="CiteAnything" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="MIT License" /></a>
</p>

## What the skill does

CiteAnything teaches an AI agent to:

1. inspect an original web page or private knowledge-base document;
2. create a replayable citation using exact text or table anchors;
3. render the citation correctly for chat, Markdown, HTML, PPTX, and PDF;
4. package source, rendered output, and `citations.json` as a durable Work;
5. create or update that Work through the first-party CiteAnything CLI.

The canonical international service is [citeanything.app](https://citeanything.app); the China service is [citeanything.cn](https://citeanything.cn).

## Install with Claude Code

```text
/plugin marketplace add veriglow/veriglow-plugins
/plugin install veriglow@veriglow-plugins
```

Restart Claude Code, then type `/` to verify that `citeanything` and `agentmap` are available.

## Other Agent Skills hosts

The skill follows the open [Agent Skills](https://agentskills.io) format. Clone the standalone skill into the skill directory used by Cursor, Gemini CLI, Codex, or another compatible host:

```bash
git clone https://github.com/veriglow/citeanything-skill.git /path/to/skills/citeanything
```

## Authentication boundaries

CiteAnything deliberately uses separate scoped keys:

- Skill Key: citations, screenshots, and KB documents (`CITEANYTHING_API_KEY`).
- SyncAnything Key: read-only local indexing.
- CLI/TUI Key: conversations, agent runs, and Work lifecycle operations.

Generate the matching key from **Take CiteAnything Home** in the account sidebar. See [references/api-key-setup.md](references/api-key-setup.md).

## Citation and Work output

- CiteAnything conversations use `[@ev:TOKEN]`; first-party clients render it as an interactive badge.
- Ordinary Markdown uses clickable citation URLs.
- Visible HTML/PPTX/PDF Works use linked green numeric badges—never raw markers or bare tokens.
- Complete token mappings remain in `citations.json` for reproducibility.
- The CiteAnything CLI, not SyncAnything, creates and updates durable Works.

See [SKILL.md](SKILL.md) for the workflow, [references/citation-api.md](references/citation-api.md) for the citation schema, and [references/works.md](references/works.md) for artifact packaging and synchronization.

## License

[MIT](LICENSE)
