#!/usr/bin/env python3
"""Render a decisions.yaml (MADR four states) into DECISIONS.md and a self-contained
decisions.html next to it.
Run: python3 -I render_decisions.py path/to/decisions.yaml"""
import os, pathlib, sys, urllib.parse, yaml

SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "decisions.yaml").resolve()
HERE = SRC.parent
src = yaml.safe_load(open(SRC, encoding="utf-8"))
meta = src.get("meta", {})
decs = src["decisions"]
TITLE = meta.get("title", "决定登记簿")
ROOT = (HERE / meta.get("root", "../..")).resolve()
SIDES = list((meta.get("sides") or {"main": "决定"}).items())
OWNER_ZH = meta.get("owners") or {}
STATE_ZH = {"proposed": "待定", "accepted": "已定", "superseded": "已替代", "rejected": "已否决"}
ORDER = ["proposed", "accepted", "superseded", "rejected"]


def lst(x):
    return x if isinstance(x, list) else ([x] if x else [])


def esc(x):
    return str(x).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def side_of(d):
    return d.get("side", SIDES[0][0])


counts = {k: sum(d["status"] == k for d in decs) for k in ORDER}
by_side = {k: [d for d in decs if side_of(d) == k] for k, _ in SIDES}

# ---------- Markdown ----------
lines = [f"# {TITLE}（更新 {src.get('updated', '')}）", "",
         "MADR 四态：待定（等谁见 owner）· 已定 · 已替代 · 已否决。真相源 `decisions.yaml`；交互版 [decisions.html](decisions.html)。", "",
         " · ".join(f"{STATE_ZH[k]} {counts[k]}" for k in ORDER), ""]
for sk, sz in SIDES:
    rows = by_side[sk]
    if not rows:
        continue
    pend = sum(d["status"] == "proposed" for d in rows)
    lines += [f"## {sz}（{len(rows)} 条，待定 {pend}）", "",
              "| ID | 状态 | 门 | 决定 | 等谁 / 日期 | 内容 | 定错了要重跑 | 证据 |", "|---|---|---|---|---|---|---|---|"]
    for d in rows:
        st = d["status"]
        who = (OWNER_ZH.get(d.get("owner"), d.get("owner", "")) + " · " if st == "proposed" else "") + str(d.get("date", ""))
        ev = "<br>".join(f"`{e}`" for e in lst(d.get("evidence")))
        extra = (" → " + d["superseded_by"]) if d.get("superseded_by") else ""
        gate = d.get("gate", "") + (f" · {d['step']}" if d.get("step") else "")
        lines.append(f"| {d['id']}{extra} | {STATE_ZH[st]} | {gate} | {d['title']} | {who} | "
                     f"{d.get('decision', '')} | {d.get('consequences', '')} | {ev} |")
    lines.append("")
(HERE / "DECISIONS.md").write_text("\n".join(lines), encoding="utf-8")


# ---------- HTML ----------
def href(rel):
    """Relative link from the yaml's folder to a project path, or None if the file is missing."""
    p = ROOT / rel
    return urllib.parse.quote(os.path.relpath(p, HERE)) if rel and p.exists() else None


def ev_item(e):
    h = href(str(e).split("#")[0])
    return f'<li><a href="{h}"><code>{esc(e)}</code></a></li>' if h else f"<li><code>{esc(e)}</code></li>"


def card(d):
    opts = "".join(f"<li>{esc(o)}</li>" for o in lst(d.get("options")))
    ev = "".join(ev_item(e) for e in lst(d.get("evidence")))
    rel = ""
    if d.get("superseded_by"):
        rel += f'<p class="rel">被 <b>{esc(d["superseded_by"])}</b> 替代</p>'
    if d.get("supersedes"):
        rel += '<p class="rel">替代 ' + ", ".join(esc(x) for x in lst(d["supersedes"])) + "</p>"
    own = (f'<span class="own">等 {esc(OWNER_ZH.get(d.get("owner"), d.get("owner", "")))}</span>'
           if d["status"] == "proposed" else "")
    step = f'<span class="stp">{esc(d["step"])}</span>' if d.get("step") else ""
    ctx = f'<p class="ctx"><b>背景</b> {esc(d["context"])}</p>' if d.get("context") else ""
    cons = f'<p><b>后果 / 定错了要重跑</b> {esc(d["consequences"])}</p>' if d.get("consequences") else ""
    return (f'<article class="card s-{d["status"]}" data-status="{d["status"]}" data-owner="{esc(d.get("owner", ""))}">'
            f'<header><span class="id">{esc(d["id"])}</span>{step}<span class="gate">{esc(d.get("gate", ""))}</span>'
            f'<span class="st">{STATE_ZH[d["status"]]}</span>{own}<span class="date">{esc(d.get("date", ""))}</span></header>'
            f'<h3>{esc(d["title"])}</h3>{ctx}'
            + (f"<p><b>选项</b></p><ul>{opts}</ul>" if opts else "")
            + f'<p class="dec"><b>决定</b> {esc(d.get("decision", ""))}</p>{cons}{rel}'
            + (f'<p><b>证据</b></p><ul class="ev">{ev}</ul>' if ev else "")
            + "</article>")


sections = []
for sk, sz in SIDES:
    rows = by_side[sk]
    if not rows:
        continue
    pend = sum(d["status"] == "proposed" for d in rows)
    sections.append(f'<section class="side" data-side="{esc(sk)}"><h2>{esc(sz)} <small>{len(rows)} 条 · 待定 {pend}</small></h2>'
                    f'<div class="grid">{"".join(card(d) for d in rows)}</div></section>')

CSS = """
:root{--bg:#f7f8fa;--fg:#1d2330;--mut:#6b7280;--card:#fff;--line:#e5e7eb;--p:#d97706;--a:#059669;--s:#6b7280;--r:#dc2626}
@media (prefers-color-scheme: dark){:root{--bg:#0f1115;--fg:#e5e7eb;--mut:#9ca3af;--card:#171a21;--line:#2a2f3a}}
body{margin:0;padding:24px 16px;font:15px/1.55 -apple-system,"PingFang SC","Noto Sans CJK SC",sans-serif;background:var(--bg);color:var(--fg)}
h1{font-size:22px;margin:0 0 4px}h2{font-size:18px;margin:26px 0 10px;padding-bottom:6px;border-bottom:2px solid var(--line)}h2 small{color:var(--mut);font-weight:400;font-size:13px}
.sub{color:var(--mut);margin-bottom:16px}
.bar{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px}.bar button{border:1px solid var(--line);background:var(--card);color:var(--fg);padding:6px 12px;border-radius:999px;cursor:pointer}.bar button.on{outline:2px solid var(--fg)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(360px,100%),1fr));gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-left:5px solid var(--s);border-radius:10px;padding:14px 16px}
.card.s-proposed{border-left-color:var(--p)}.card.s-accepted{border-left-color:var(--a)}.card.s-rejected{border-left-color:var(--r)}.card.s-superseded{opacity:.75}
header{display:flex;gap:8px;flex-wrap:wrap;align-items:center;font-size:12px;color:var(--mut)}.id{font-weight:700;color:var(--fg)}.st{padding:1px 8px;border-radius:999px;border:1px solid var(--line)}.own{color:var(--p);font-weight:600}
h3{margin:6px 0 8px;font-size:16px}p{margin:6px 0}ul{margin:2px 0 8px 18px;padding:0}.ev code{font-size:12px}.ev a{color:inherit}.dec{background:rgba(5,150,105,.08);padding:6px 8px;border-radius:6px}.rel{color:var(--mut);font-size:13px}
.hide{display:none}
.stp{padding:1px 8px;border-radius:999px;background:rgba(37,99,235,.12);color:#2563eb;font-weight:600}
"""
JS = """
var bar=document.getElementById('bar');bar.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;
var grp=b.dataset.g;bar.querySelectorAll('button[data-g="'+grp+'"]').forEach(function(x){x.classList.toggle('on',x===b)});apply();});
function apply(){var st=bar.querySelector('button.on[data-g="s"]').dataset.f,sd=bar.querySelector('button.on[data-g="d"]').dataset.f;
document.querySelectorAll('.card').forEach(function(c){var show=true;if(st!=='all'){var kv=st.split(':');show=c.dataset[kv[0]]===kv[1]&&(kv[0]!=='owner'||c.dataset.status==='proposed');}c.classList.toggle('hide',!show);});
document.querySelectorAll('section.side').forEach(function(s){var sideok=(sd==='all'||s.dataset.side===sd);var any=s.querySelectorAll('.card:not(.hide)').length>0;s.classList.toggle('hide',!(sideok&&any));});}
"""
sub = (f"更新 {esc(src.get('updated', ''))} · " + " · ".join(f"{STATE_ZH[k]} {counts[k]}" for k in ORDER) + " · 真相源 decisions.yaml")
btn_s = ('<button data-g="s" data-f="all" class="on">全部状态</button>'
         + "".join(f'<button data-g="s" data-f="status:{k}">{STATE_ZH[k]}</button>' for k in ORDER)
         + "".join(f'<button data-g="s" data-f="owner:{esc(k)}">等{esc(v)}</button>' for k, v in OWNER_ZH.items()))
btn_d = ('<button data-g="d" data-f="all" class="on">全部</button>'
         + "".join(f'<button data-g="d" data-f="{esc(k)}">{esc(v)}</button>' for k, v in SIDES))
html = ("<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
        f"<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{esc(TITLE)}</title>"
        f"<style>{CSS}</style></head><body><h1>{esc(TITLE)}</h1><div class=\"sub\">{sub}</div>"
        f"<div class=\"bar\" id=\"bar\">{btn_s}<span style=\"width:16px\"></span>{btn_d}</div>"
        f"{''.join(sections)}<script>{JS}</script></body></html>")
(HERE / "decisions.html").write_text(html, encoding="utf-8")
print(f"wrote {HERE / 'DECISIONS.md'} and {HERE / 'decisions.html'} ({len(decs)} decisions)")
