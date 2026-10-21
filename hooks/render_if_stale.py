#!/usr/bin/env python3
"""PostToolUse hook: re-render every decisions.yaml whose decisions.html is missing or older.
Only files with a top-level "decisions:" key count, so unrelated decisions.yaml files are left alone.
Standard library only; the renderer runs under DECISION_REGISTER_PYTHON (default: this Python),
which needs PyYAML. A render failure exits 2 so Claude sees the error."""
import os, pathlib, subprocess, sys

PY = os.environ.get("DECISION_REGISTER_PYTHON", sys.executable)
RENDER = pathlib.Path(__file__).resolve().parent.parent / "skills/decision-register/scripts/render_decisions.py"
ROOT = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
SKIP = {".git", "node_modules", ".venv", "__pycache__"}

failed = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP]
    if len(pathlib.Path(dirpath).relative_to(ROOT).parts) >= 5:
        dirnames[:] = []
    if "decisions.yaml" not in filenames:
        continue
    y = pathlib.Path(dirpath) / "decisions.yaml"
    h = y.with_name("decisions.html")
    if h.exists() and h.stat().st_mtime >= y.stat().st_mtime:
        continue
    if not any(line.startswith("decisions:") for line in y.read_text(encoding="utf-8", errors="ignore").splitlines()):
        continue
    r = subprocess.run([PY, "-I", str(RENDER), str(y)], capture_output=True, text=True)
    if r.returncode:
        failed.append(f"{y}: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else 'exit ' + str(r.returncode)}")

if failed:
    print("decision-register: rendering failed:\n" + "\n".join(failed)
          + "\nIf PyYAML is missing, install it or set DECISION_REGISTER_PYTHON.", file=sys.stderr)
    sys.exit(2)
