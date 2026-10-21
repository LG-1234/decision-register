# decision-register

A Claude Code plugin that keeps a project's decisions in one YAML file
(MADR-style four states: proposed / accepted / superseded / rejected) and renders
them into a Markdown table and a filterable, self-contained HTML page.
A bundled hook re-renders the page whenever `decisions.yaml` changes.

一个 Claude Code plugin：把项目里所有判断记在一个 `decisions.yaml` 里（待定 / 已定 / 已替代 / 已否决），
生成 Markdown 表格和可筛选的 HTML 页面。自带 hook：yaml 一改，页面自动更新。
被问到"这个之前定过吗"时先查登记簿，不重复讨论。

## Install (plugin, with the hook)

In Claude Code:

```
/plugin marketplace add <owner>/decision-register
/plugin install decision-register@decision-register
```

Requires Python 3 with PyYAML. If your default `python3` lacks PyYAML, point the hook at one that has it:

```bash
export DECISION_REGISTER_PYTHON=/path/to/python3
```

## Install (skill only, no hook)

```bash
git clone <this repo> /tmp/decision-register
cp -R /tmp/decision-register/skills/decision-register ~/.claude/skills/
```

For Codex, copy into `~/.codex/skills/` instead. Without the plugin there is no hook, so render by hand after each change.

## Quick start

```bash
S=~/.claude/skills/decision-register   # or the plugin's skills/decision-register folder
mkdir -p docs/status
cp $S/templates/decisions.example.yaml docs/status/decisions.yaml
python3 -I $S/scripts/render_decisions.py docs/status/decisions.yaml
python3 -I $S/scripts/check_decisions.py docs/status/decisions.yaml
```

Edit `meta.sides` and `meta.owners` in the YAML to fit your project. See
[skills/decision-register/SKILL.md](skills/decision-register/SKILL.md) for the field rules.

## How the hook works

`hooks/render_if_stale.py` runs after every Edit / Write / Bash tool call. It walks the
project (up to 5 levels, skipping `.git`, `node_modules`, `.venv`), and for each
`decisions.yaml` with a top-level `decisions:` key whose `decisions.html` is missing or
older, it runs the renderer. A failed render exits with code 2, so Claude sees the error.

## License

MIT
