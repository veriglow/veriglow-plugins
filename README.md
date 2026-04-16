<p align="center">
  <img src="https://brand.veri-glow.com/logo-green-transparent.svg" width="80" alt="VeriGlow Logo" />
</p>

<h1 align="center">VeriGlow Plugins</h1>

<p align="center">
  <strong>Claude Code plugin marketplace by VeriGlow</strong><br>
  Verifiable citations and data extraction for AI agents.
</p>

---

## Install

```
/plugin marketplace add veriglow/veriglow-plugins
/plugin install veriglow@veriglow-plugins
```

Restart Claude Code. Then type `/` to verify the `citeanything` and `agentmap` skills are available.

## What's included

The `veriglow` plugin bundles:

- **[CiteAnything](https://github.com/veriglow/citeanything-skill)** skill — create verifiable citations for every claim, with clickable source links that open highlighted evidence
- **[AgentMap](https://github.com/veriglow/agentmap-skill)** skill — look up data-extraction recipes for any website (internal APIs, selectors, automation steps)
- **Auto-save hook** — every response and its citations are automatically saved to `~/.citeanything/history/` (no manual config needed)

## Standalone skills (for non-Claude Code users)

The same skills are also available as independent repos for any Agent Skills–compatible tool (Cursor, Gemini CLI, etc.):

- [citeanything-skill](https://github.com/veriglow/citeanything-skill)
- [agentmap-skill](https://github.com/veriglow/agentmap-skill)

## License

[MIT](LICENSE)
