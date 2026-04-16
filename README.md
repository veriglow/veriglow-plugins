<p align="center">
  <img src="https://brand.veri-glow.com/logo-green-transparent.svg" width="80" alt="VeriGlow Logo" />
</p>

<h1 align="center">VeriGlow Plugins</h1>

<p align="center">
  <strong>Take CiteAnything home with you.</strong><br>
  Verifiable citations and data extraction recipes, for any AI agent you use.
</p>

---

## Choose your setup

Pick the path that matches your AI agent:

- [**Claude Code** — one-click plugin (recommended)](#claude-code)
- [**Cursor, Gemini CLI, VS Code Copilot, or other agents** — standalone skills](#other-agents)
- [**Already using the old standalone skills on Claude Code?** — migrate to the plugin](#migrating-from-standalone-skills)

---

## Claude Code

One command installs both skills, registers the auto-save hook, and you're done:

```
/plugin marketplace add veriglow/veriglow-plugins
/plugin install veriglow@veriglow-plugins
```

Restart Claude Code. Then type `/` to verify `citeanything` and `agentmap` are available.

**What's included:**

- **[CiteAnything](https://github.com/veriglow/citeanything-skill)** skill — create verifiable citations for every claim, with clickable source links that open highlighted evidence
- **[AgentMap](https://github.com/veriglow/agentmap-skill)** skill — look up data-extraction recipes for any website (internal APIs, selectors, automation steps)
- **Auto-save hook** — every response and its citations are automatically saved to `~/.citeanything/history/` (no manual config needed)

---

## Other agents

The Claude Code plugin format isn't compatible with other agents, but both skills follow the open [Agent Skills](https://agentskills.io) specification. Clone them into your agent's skills directory:

**Cursor**
```bash
git clone https://github.com/veriglow/citeanything-skill.git ~/.cursor/skills/citeanything
git clone https://github.com/veriglow/agentmap-skill.git ~/.cursor/skills/agentmap
```

**Gemini CLI / other Agent Skills–compatible tools**

Clone into whatever skills directory your agent uses (`~/.gemini/skills/`, etc.).

**Note:** Without the plugin wrapper, auto-save to `~/.citeanything/history/` won't run. You can manually set up the Stop hook if your agent supports one — see [citeanything-skill/references/api-key-setup.md](https://github.com/veriglow/citeanything-skill/blob/main/references/api-key-setup.md).

---

## Migrating from standalone skills

If you previously installed `citeanything-skill` or `agentmap-skill` by cloning them into `~/.claude/skills/`, switch to the plugin for auto-save and easier updates:

**1. Remove the old standalone skills**

```bash
rm -rf ~/.claude/skills/citeanything ~/.claude/skills/agentmap
```

**2. Install the plugin**

```
/plugin marketplace add veriglow/veriglow-plugins
/plugin install veriglow@veriglow-plugins
```

**3. (Optional) Remove your manual Stop hook config**

If you previously added a `Stop` hook to `~/.claude/settings.json` pointing to `citeanything-skill/hooks/save-history.sh`, remove that entry — the plugin registers the hook automatically.

**Restart Claude Code.** You're done. Skills keep the same names (`citeanything`, `agentmap`) so any CLAUDE.md rules you wrote still apply.

---

## License

[MIT](LICENSE)
