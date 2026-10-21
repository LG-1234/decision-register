# decision-register

A Claude Code / Codex skill that keeps a project's decisions in one YAML file
(MADR-style four states: proposed / accepted / superseded / rejected) and renders
them into a Markdown table and a filterable, self-contained HTML page.

一个 Claude Code / Codex skill：把项目里所有判断记在一个 `decisions.yaml` 里（待定 / 已定 / 已替代 / 已否决），
自动生成 Markdown 表格和可筛选的 HTML 页面。被问到"这个之前定过吗"时先查登记簿，不重复讨论。

## Install

```bash
git clone <this repo> ~/.claude/skills/decision-register
```

(For Codex, clone into `~/.codex/skills/decision-register`.) Requires Python 3 and PyYAML.

## Quick start

```bash
mkdir -p docs/status
cp ~/.claude/skills/decision-register/templates/decisions.example.yaml docs/status/decisions.yaml
python3 -I ~/.claude/skills/decision-register/scripts/render_decisions.py docs/status/decisions.yaml
python3 -I ~/.claude/skills/decision-register/scripts/check_decisions.py docs/status/decisions.yaml
```

Edit `meta.sides` and `meta.owners` in the YAML to fit your project. See [SKILL.md](SKILL.md) for the field rules.

## License

MIT
