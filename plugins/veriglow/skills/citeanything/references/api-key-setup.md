# CiteAnything authentication setup

## Choose the site

- International: `https://citeanything.app`
- China: `https://citeanything.cn`

Set `CITEANYTHING_BASE_URL` only when using the China site or a custom deployment. The international site is the default.

## Generate the right key

Log in, open **Take CiteAnything Home** in the account sidebar, and choose the action that matches the client:

| Action | Local variable/client | Granted capability |
|---|---|---|
| **Generate Skill Key** | `CITEANYTHING_API_KEY` | `citation`, `kb`, `screenshot` |
| **Connect SyncAnything** | `SYNCANYTHING_CITEANYTHING_API_KEY` | `context.read`, `works.read` |
| **Connect CLI / TUI** | `citeanything auth connect` or `CITEANYTHING_CLI_API_KEY` | conversations, agent runs, Works, citations, and KB |

Keys start with `ca_`, are shown in full only once, and can be revoked from the account. Never ask for the user's password. Do not paste a key into source code, a Work directory, chat output, or a committed environment file.

## Configure the citation skill

Set the Skill Key in the environment that launches the agent:

```bash
export CITEANYTHING_API_KEY="ca_..."
# Only for the China site:
export CITEANYTHING_BASE_URL="https://citeanything.cn"
```

Verify without printing the key:

```bash
CITEANYTHING_BASE="${CITEANYTHING_BASE_URL:-https://citeanything.app}"
curl --fail-with-body -sS "$CITEANYTHING_BASE/api/auth/me" \
  -H "Authorization: Bearer $CITEANYTHING_API_KEY"
```

If the response is HTTP 403 with a required scope, the wrong client key was supplied. Generate a Skill Key instead of broadening or reusing another key.

## Configure the CLI/TUI

Prefer the hidden interactive connection flow:

```bash
citeanything auth connect --site international
citeanything auth status
```

Use `--site china` for the China site. Native `auth connect` currently saves metadata under `~/.citeanything/connections.json` and stores its secret in macOS Keychain. On other platforms, or for non-interactive automation, inject `CITEANYTHING_CLI_API_KEY` through the secure runtime and optionally set `CITEANYTHING_BASE_URL`.

## Enable automatic skill use

If the user wants all externally grounded answers cited, add an instruction equivalent to this to the agent's durable project/user instructions:

```text
When an answer uses web research or external factual claims, use the citeanything skill to create citations from inspected original sources.
```

Do not modify durable instructions without the user's approval.

## Claude Code history hook

The VeriGlow plugin registers its Stop hook automatically. It saves the latest cited exchange to `${CITEANYTHING_HISTORY_DIR:-~/.citeanything/history}` and recognizes both canonical `citeanything.app` links and `[@ev:TOKEN]` markers.

For a standalone skill installation, register `hooks/save-history.sh` manually only if the host supports Claude Code-style Stop hooks. Ask where the user wants local history before enabling it. A custom location must be set persistently in the environment that launches the host:

```bash
export CITEANYTHING_HISTORY_DIR="$HOME/Documents/citeanything-history"
```

Restart the host after changing persistent environment variables. Local history is a convenience copy; CiteAnything remains the source of truth for its own cloud conversations and Works.
