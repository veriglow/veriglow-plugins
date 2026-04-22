<p align="center">
  <img src="https://brand.veri-glow.com/logo-green-transparent.svg" width="80" alt="VeriGlow Logo" />
</p>

<h1 align="center">CiteAnything</h1>

<p align="center">
  <strong>Verifiable evidence citations for AI agents</strong><br>
  Every claim backed by a source. Every source one click away.
</p>

<p align="center">
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/Agent_Skills-compatible-10B981?style=flat-square" alt="Agent Skills compatible" /></a>
  <a href="https://citeanything.veri-glow.com"><img src="https://img.shields.io/badge/demo-citeanything.veri--glow.com-10B981?style=flat-square" alt="Demo" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="MIT License" /></a>
</p>

---

> 💡 Using Claude Code? Install via the [veriglow plugin](https://github.com/veriglow/veriglow-plugins) for a one-command setup with auto-save.

---

## What it does

CiteAnything is an [Agent Skill](https://agentskills.io) that teaches AI agents to create **verifiable, replayable citations** for every data claim they make.

When an agent uses this skill:
1. It fetches data from a web page or uploaded document
2. It creates a citation record with the exact source text
3. It embeds a clickable link in its response
4. The user clicks the link → the original source opens with the cited text **highlighted**

<p align="center">
  <em>Try it:</em> <a href="https://citeanything.veri-glow.com/e/nAPwrQ2r">citeanything.veri-glow.com/e/nAPwrQ2r</a>
</p>

## Quick start

### Option 1: Any agent that supports Agent Skills

Install CiteAnything together with [AgentMap](https://github.com/veriglow/agentmap-skill) (recommended — AgentMap finds data, CiteAnything cites it):

```bash
# Claude Code — install both skills
git clone https://github.com/veriglow/citeanything-skill.git ~/.claude/skills/citeanything
git clone https://github.com/veriglow/agentmap-skill.git ~/.claude/skills/agentmap
```

> **Note:** Restart Claude Code after installing for the skills to appear. Type `/` to verify `citeanything` and `agentmap` are in the list.

```bash
# Cursor
git clone https://github.com/veriglow/citeanything-skill.git .cursor/skills/citeanything
git clone https://github.com/veriglow/agentmap-skill.git .cursor/skills/agentmap
```

### Option 2: Claude Code via Plugin Marketplace

```bash
/plugin marketplace add veriglow/veriglow-skills
# Then install the citeanything plugin from the marketplace
```

## Skill structure

```
citeanything-skill/
├── SKILL.md                                # Skill instructions (API contract, workflow, examples)
├── references/
│   └── pdf2htmlex-structure.md              # PDF→HTML structure guide (loaded on demand)
├── scripts/
│   └── local-kb.py                          # Local privacy mode: PDF→HTML + localhost server
├── LICENSE
└── README.md
```

Follows the [Agent Skills specification](https://agentskills.io/specification) with three-layer progressive disclosure:

| Layer | File | Loaded when |
|-------|------|-------------|
| 1. Metadata | `SKILL.md` frontmatter | Always (name + description) |
| 2. Instructions | `SKILL.md` body | Skill is activated |
| 3. References | `references/`, `scripts/` | Agent reads on demand |

## Two citation modes

### Web citations

Agent fetches data from any website → creates citation → user clicks to see source with highlighted text.

```
Revenue was $94.8B [source](https://citeanything.veri-glow.com/e/a1b2c3d4)
                    ↑ click → opens source page with text highlighted
```

### KB document citations

Upload a PDF → server converts to browsable HTML → agent extracts text → creates citation with page-level positioning.

**Server mode**: PDF uploaded to CiteAnything server (shareable, verifiable by anyone)

**Local mode** *(optional)*: PDF stays on your machine, converted locally via Docker + pdf2htmlEX. Requires Docker. See `scripts/local-kb.py`.

## API

All citations go through one endpoint:

```
POST https://citeanything.veri-glow.com/api/citation
```

See [SKILL.md](SKILL.md) for the complete API contract, request fields, and examples.

## Compatibility

This skill follows the open [Agent Skills](https://agentskills.io) standard and works with:

- [Claude Code](https://claude.ai/code) — via skill directory or plugin marketplace
- [Cursor](https://cursor.com) — via `.cursor/skills/`
- [GitHub Copilot](https://github.com/features/copilot) — via agent skills support
- [Gemini CLI](https://geminicli.com) — via skills directory
- [VS Code](https://code.visualstudio.com) — via Copilot agent skills
- Any other agent that supports the Agent Skills format

## Built by

<a href="https://veri-glow.com">
  <img src="https://brand.veri-glow.com/favicon.svg" width="20" alt="VeriGlow" />
  <strong>VeriGlow</strong>
</a>

## License

[MIT](LICENSE)
