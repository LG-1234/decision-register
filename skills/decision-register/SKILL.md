---
name: decision-register
description: 维护项目的决定登记簿（MADR 四态：待定 / 已定 / 已替代 / 已否决）：decisions.yaml → DECISIONS.md / decisions.html。在以下情况使用：用户问"这个之前定过吗 / 为什么这样定 / 还有哪些待定"；做出、改变、替代或否决任何项目判断（数据、模型、估计、扩展、仓库约定等）；开会前导出待定项；发现别的文档里的决定和登记簿不一致。
---

# 决定登记簿（decision register）

**结论先行。**登记簿是项目所有判断的唯一真相源。被问到判断时，先查登记簿，已定的直接引用 ID 和证据，不重新讨论。做出新判断，或已有判断改变时，在同一轮里写进 `decisions.yaml`，然后重新生成页面并核对。

## 文件

默认放在项目的 `docs/status/`（可以换位置，脚本都接受路径参数）。

| 文件 | 作用 | 谁来改 |
|---|---|---|
| `decisions.yaml` | 真相源 | 手工编辑 |
| `DECISIONS.md`、`decisions.html` | 生成的页面 | 不要手改 |
| `<skill>/scripts/render_decisions.py` | 渲染脚本 | 只在改版式时改 |
| `<skill>/scripts/check_decisions.py` | 核对脚本 | — |

第一次使用：把 `templates/decisions.example.yaml` 复制成项目里的 `decisions.yaml`，按项目改 `meta` 里的 `sides` 和 `owners`。

## 1. 查

- 按关键词、`gate`、`step` 或 `side` 搜 `decisions.yaml`。
- 回答时写明 ID、状态和证据路径。例如："D14-B 已定（2026-10-20），证据见 `docs/methods/weights.md`"。
- 如果查到的内容和对话或其他文档矛盾，先报告这个矛盾，不要直接按其中一方行动。

## 2. 写（新增或修改一条）

每条决定是一张卡，字段如下：

| 字段 | 规则 |
|---|---|
| `id` | 顺延到下一个 `Dnn`。被替代的旧版加后缀，例如 `D01-old`；同一问题的另一个选项用 `D14-B` |
| `side` | 取 `meta.sides` 里的键，例如 `data` / `model` / `estimation` / `extension` / `repo` |
| `step` | 可选。决定落在流程的哪一步（例如 `Step04`）。`meta.require_step_for` 里列出的 side 必填 |
| `gate` | 可选。对应的门禁或检查点编号 |
| `title` | 一句话，写问题本身或选定的结果 |
| `status` | `proposed`（待定）/ `accepted`（已定）/ `superseded`（已替代）/ `rejected`（已否决） |
| `date` | 绝对日期，例如 2026-10-21。不要写"今天"或"上周" |
| `owner` | 取 `meta.owners` 里的键，例如 `user` / `supervisor` / `team`。待定时写等谁 |
| `context` | 背景和关键数字 |
| `options` | 列表，写清每个选项的代价 |
| `decision` | 待定时写"未定"，并给出建议；已定时写定了什么 |
| `consequences` | 定错了要重跑或返工什么 |
| `evidence` | **只写文件路径（相对项目根目录，可加 `#节`）或 commit**，不写聊天记录 |
| `supersedes` / `superseded_by` | 替代关系**两边都要写**：新卡写 `supersedes: [旧ID]`，旧卡改为 `status: superseded` 并写 `superseded_by: 新ID` |

### `step` 怎么定

按"这条决定改的是哪一步的产物"来归，不按"它影响到哪里"来归。变量或口径在哪一步构造，就归哪一步，即使它主要影响下游。拿不准时，把两种归法都告诉用户，让用户定。

规则：
- **状态改成 accepted、superseded 或 rejected，必须有用户的原话。**在 `context` 或 `decision` 里写明是谁、在哪天定的。只有别人（如导师、负责人）能定的事，`owner` 写对方，不要替对方定。
- 推翻一个已定的决定时，新开一张卡，或者恢复被否决的那张卡，把旧卡标为已替代，并写出**更正理由**。不要直接改写旧卡的内容。
- 同一轮里，同时改其他文档中同一个决定的记录，避免两边说法不一致。
- 更新文件顶部的 `updated:` 时间。

## 3. 渲染

**以 plugin 安装时会自动渲染。**plugin 自带一个 PostToolUse hook：每次 Edit、Write 或 Bash 之后，只要项目里某个 `decisions.yaml` 比旁边的 `decisions.html` 新（或 HTML 还不存在），就重新渲染。渲染失败时 hook 会把错误报给你，必须先修好再继续。

以下情况要手动运行：只装了 skill 没装 plugin、用 Codex 或手工改了 yaml、改了渲染脚本。

```bash
python3 -I <skill>/scripts/render_decisions.py docs/status/decisions.yaml
```

在 yaml 同目录生成 `DECISIONS.md` 和 `decisions.html`。证据路径相对 `meta.root`（默认是 yaml 往上两级）解析；文件存在就变成链接。

hook 只保证"yaml 改了，页面就更新"。决定只在对话里说了、没写进 yaml，hook 不会知道，所以第 2 节的"同一轮写进 yaml"仍然是硬规则。

## 4. 核对（每次写完都做）

```bash
python3 -I <skill>/scripts/check_decisions.py docs/status/decisions.yaml
```

检查：ID 不重复、状态合法、必填 `step` 不缺、替代关系两边一致、`decisions.html` 里的链接都存在。

## 5. 会前导出

把某个 `owner`（如 `supervisor`）且 `status: proposed` 的条目列出来，附上 `context`、`options` 和建议。页面上的"等 …"筛选按钮也能看到这些条目。

## 常见错误

- 只在对话里说"已定"，没有写进 yaml。下一个会话会把旧状态当成真的。
- 替代关系只写了一边。
- `evidence` 写了"见对话"或会话 ID。
- 必填 `step` 的一侧没有标 `step`。
- 用别的工具改了 yaml，却忘了重新渲染。
