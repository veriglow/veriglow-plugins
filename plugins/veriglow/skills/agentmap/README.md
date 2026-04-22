<p align="center">
  <img src="https://brand.veri-glow.com/logo-green-transparent.svg" width="80" alt="VeriGlow Logo" />
</p>

<h1 align="center">AgentMap</h1>

<p align="center">
  <strong>Discover hidden APIs behind any website</strong><br>
  Structured data extraction specs for AI agents — 65 data sources indexed.
</p>

<p align="center">
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/Agent_Skills-compatible-10B981?style=flat-square" alt="Agent Skills compatible" /></a>
  <a href="https://agentmap.veri-glow.com"><img src="https://img.shields.io/badge/browse-agentmap.veri--glow.com-10B981?style=flat-square" alt="Browse maps" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="MIT License" /></a>
</p>

---

> 💡 Using Claude Code? Install via the [veriglow plugin](https://github.com/veriglow/veriglow-plugins) for a one-command setup.

---

## What it does

AgentMap is an [Agent Skill](https://agentskills.io) that gives AI agents a registry of reverse-engineered API specs for websites. Instead of scraping HTML or automating browsers, agents look up the hidden API behind a web page and call it directly.

Each "map" documents:
- **API endpoint** — URL, method, parameters, response schema
- **Browser automation fallback** — action steps, DOM selectors, JS controllers
- **Agent reports** — real-world success rates, edge cases, workarounds

### Example

```bash
# Agent needs Shanghai Stock Exchange bond data
# Step 1: Look up the map
curl -s "https://agentmap.veri-glow.com/www.sse.com.cn/market/bonddata/overview/day"

# Step 2: Map tells agent the hidden API endpoint
curl "https://www.sse.com.cn/js/common/sseBond498Fixed.js?searchDate=2025-02-11"

# → Structured JSON with 17 bond categories × 4 trading metrics
```

## Quick start

### Install

```bash
# Claude Code
git clone https://github.com/veriglow/agentmap-skill.git ~/.claude/skills/agentmap

# Cursor
git clone https://github.com/veriglow/agentmap-skill.git .cursor/skills/agentmap
```

> **Note:** Restart your agent after installing. For Claude Code, type `/` to verify `agentmap` appears in the skill list.

### Recommended: install with CiteAnything

AgentMap pairs with [CiteAnything](https://github.com/veriglow/citeanything-skill) — AgentMap finds the data, CiteAnything creates verifiable citations for it.

```bash
# Install both skills together
git clone https://github.com/veriglow/agentmap-skill.git ~/.claude/skills/agentmap
git clone https://github.com/veriglow/citeanything-skill.git ~/.claude/skills/citeanything
```

## How to query

Strip the protocol from the target URL and prepend `agentmap.veri-glow.com/`:

```
Target:   https://www.sse.com.cn/market/bonddata/overview/day/
Query:    https://agentmap.veri-glow.com/www.sse.com.cn/market/bonddata/overview/day
```

- Keep `www.` if the original URL has it
- Remove trailing slash
- Returns JSON for agents, HTML for browsers (content negotiation)

## Coverage

**65 data sources** currently indexed:

| Region | Sources | Examples |
|--------|---------|----------|
| China (SSE) | 55 maps | Stock data, bond trading, fund overview, margin trading, index data |
| US (FRED) | 6 maps | GDP, CPI, Treasury yields, Fed Funds Rate, unemployment |
| International | 4 maps | Crypto (CoinPaprika), weather (Open-Meteo), Hacker News |

See [SKILL.md](SKILL.md) for the full list with URLs.

## Compatibility

Works with any agent that supports [Agent Skills](https://agentskills.io):

Claude Code, Cursor, GitHub Copilot, Gemini CLI, VS Code, OpenAI Codex, and more.

## Built by

<a href="https://veri-glow.com">
  <img src="https://brand.veri-glow.com/favicon.svg" width="20" alt="VeriGlow" />
  <strong>VeriGlow</strong>
</a>

## License

[MIT](LICENSE)
