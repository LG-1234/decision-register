#!/usr/bin/env python3
"""Check a decisions.yaml and the decisions.html rendered next to it.
Run: python3 -I check_decisions.py path/to/decisions.yaml"""
import pathlib, re, sys, urllib.parse, yaml

SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "decisions.yaml").resolve()
src = yaml.safe_load(open(SRC, encoding="utf-8"))
meta = src.get("meta", {})
d = src["decisions"]
ids = [x["id"] for x in d]
assert len(ids) == len(set(ids)), "重复 ID"
bad_st = [x["id"] for x in d if x["status"] not in ("proposed", "accepted", "superseded", "rejected")]
assert not bad_st, f"非法 status: {bad_st}"
need = set(meta.get("require_step_for") or [])
miss = [x["id"] for x in d if x.get("side") in need and not x.get("step")]
assert not miss, f"缺 step: {miss}"
byid = {x["id"]: x for x in d}
for x in d:
    if x.get("superseded_by"):
        assert x["status"] == "superseded" and x["superseded_by"] in byid, f"替代关系不一致: {x['id']}"
    for old in x.get("supersedes") or []:
        assert byid.get(old, {}).get("superseded_by") == x["id"], f"{x['id']} 替代 {old}，但 {old} 没写 superseded_by"
html = SRC.parent / "decisions.html"
if html.exists():
    h = html.read_text(encoding="utf-8")
    dead = [l for l in set(re.findall(r'href="([^"]+)"', h))
            if not (SRC.parent / urllib.parse.unquote(l)).resolve().exists()]
    assert not dead, f"失效链接: {dead}"
    if html.stat().st_mtime < SRC.stat().st_mtime:
        print("提示：decisions.html 比 decisions.yaml 旧，需要重新渲染")
print("OK", len(ids), "条")
