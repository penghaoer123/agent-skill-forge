---
name: skill-refactor
description: >
  Hermes 技能工程统一入口——新建规范技能、重构现有技能、审计评分、补协议层。
  当用户说"新建skill""创建技能""重构这个技能""这个skill太长了""拆分skill"
  "按规范改技能""给xxx加协议层""技能审计""skill review"时使用。
  从第一行就遵循 ~/.hermes/docs/hermes-skill-refactoring-spec-v1.md（含 v1.2 系统级 Blocking Invariants + Pre-flight Gates + State Caching）。
  不要在只是微调一句话（直接 patch）或为 Hermes Agent 仓库贡献技能（那个走 hermes-agent → references/skill-authoring.md）时加载。
category: workflow
tags: [skill-engineering, skill-refactoring, skill-creation, audit]
type: skill
---

# Skill Refactor · 技能工程统一入口

> 2026-06-13 建立 · 消化自 Anthropic Skills 方法论 + 内部审计 + Codex 审查
| `references/scoring-checklist.md` | 执行 §A2 评分时 |
| `references/design-philosophy.md` | 需要判断"硬 gate vs 信任判断"时——四学派对比与决策框架 |
| `~/.hermes/docs/hermes-skill-refactoring-spec-v1.md` | 需要完整规范时 |

> 本技能已开源

| 字段 | 内容 |
|------|------|
| **Use when** | 用户说"新建skill""创建技能""重构这个技能""拆分skill""按规范改""给xxx加协议层""技能审计"；或技能超过 450 行、缺协议层、description 不够 pushy；或需要从零建一个规范技能 |
| **Do NOT use when** | 只是微调一句话（直接 patch）；为 Hermes Agent 官方仓库贡献技能（→ `hermes-agent` → `references/skill-authoring.md`） |
| **Delegate to** | 花生酱自己执行（需要判断和设计决策） |
| **Reads knowledge** | 读取目标 SKILL.md（如有）；读取重构规范；写入新/重构后的 SKILL.md + references/ |
| **Done when** | SKILL.md ≤500 行、协议层到位、决策树到位、references 带元信息头、已验证 |

## §Handoff
- Trigger: 重构过程中发现技能应该拆成多个独立技能（不只是拆 references）；或新建技能需要先确定领域知识边界
- Target: skill-creator（需要评估-迭代循环时）或直接继续本技能
- Context: 审计结果、新技能边界建议、哪些内容该独立成技能

## 入口决策

你面对的是哪种情况？

1. **创建全新技能**（从零开始，无现有 SKILL.md） → 跳转 §E 新建
2. **重构现有技能（>500行 / 结构混乱）** → 走完整流程 §A 审计 → §B 设计 → §C 执行 → §D 验证
3. **补协议层/决策树**（行数OK但缺骨架） → §A 只查必选项 → §C 补骨架
4. **改 description**（不够 pushy） → 直接改 description，不拆文件
5. **只评估不修改** → 只跑 §A 审计，输出评分报告

---

## §E 新建（从零创建规范技能）

### E1. 问清四件事

```
1. 这个技能做什么？（一句话核心能力）
2. 什么时候触发？（用户会怎么说 / 系统什么状态）
3. 谁执行？（花生酱自己 / 委派给哪个助手）
4. 什么算完成？（交付物 / 验证条件）
```

### E2. 生成骨架

直接按此模板写 SKILL.md：

```markdown
---
name: <kebab-case>
description: >
  <做什么> + <什么时候触发>。包含触发关键词。
  不要在 <反触发场景> 时加载。
category: <分类>
tags: [<标签>]
type: skill
---

# <标题>

| `references/scoring-checklist.md` | 执行 §A2 评分时 |
| `references/design-philosophy.md` | 需要判断"硬 gate vs 信任判断"时——四学派对比与决策框架 |
| `~/.hermes/docs/hermes-skill-refactoring-spec-v1.md` | 需要完整规范时 |

> 本技能已开源

| 字段 | 内容 |
|------|------|
| **Use when** | <触发条件> |
| **Do NOT use when** | <反触发> |
| **Delegate to** | <助手名 / 花生酱自己> |
| **Reads knowledge** | <知识图谱读写> |
| **Done when** | <完成条件> |

## §Handoff
- Trigger: <什么情况下交给别的技能>
- Target: <目标技能>
- Context: <带什么上下文>

## 入口决策

你面对的是哪种情况？

1. **<场景A>** → <对应动作>
2. **<场景B>** → <对应动作>
3. **不确定** → <默认行为>

## §核心流程

<最小执行体，只写关键步骤。细节放 references。>

```text
∥ Parallel:（可并行的步骤）
  - <步骤1>
  - <步骤2>

→ Sequential:（必须串行的步骤）
  - <步骤3> only after <条件>
```

## 参考文件索引

| 文件 | 内容 | 何时加载 |
|------|------|----------|
| `references/xxx.md` | ... | ... |

## 验证与复盘

- **单次验证**：<怎么确认执行成功>
- **定期复盘**：<多久检查一次 / 什么触发复盘>
```

### E3. 需要 references 时

每个 reference 必须加 v1.1 元信息头：

```yaml
---
reference_id: xxx
title: ...
scope: ...
applies_to: [skill-refactor]
source_type: reference
staleness_risk: low
last_verified: YYYY-MM-DD
owner_skill: skill-refactor
---
```

### E4. 新建后验证

执行 §D 验证步骤。新建技能必须一次通过所有必选项。

---

## §A 审计

### A1. 必选项检查（4 项，缺一不可）

| # | 检查项 | 标准 |
|---|--------|------|
| 1 | **协议层** | 5 行骨架全部到位 |
| 2 | **入口决策树** | 第一屏有决策树，覆盖主要场景 + "不确定"默认分支 |
| 3 | **Description pushy** | 包含触发关键词 + 反触发信息 |
| 4 | **500 行上限** | SKILL.md ≤ 500 行 |

### A2. 9 原则评分（1-5）

详见 `references/scoring-checklist.md`。逐项打分，输出平均分和最弱 3 项。

### A3. 输出审计报告

```markdown
## 审计报告：<技能名>
| 指标 | 值 |
|------|-----|
| SKILL.md 行数 | xxx |
| 协议层 | ✅/❌ |
| 入口决策树 | ✅/❌（x 分支） |
| Description pushy | ✅/❌ |
| 500 行上限 | ✅/❌ |
| 9 原则均分 | x.x/5 |
```

---

## §B 设计拆分方案

对超标技能（>450 行），扫描全文，按主题切分：

**留在入口的**：协议层、决策树、最小执行流程、关键原则（≤5条）、reference 索引
**拆到 references/ 的**：详细步骤、代码示例、历史 changelog、领域知识细节、长表格

输出拆分方案表：

| 内容 | 去向 | 理由 |
|------|------|------|
| ... | references/xxx.md | ... |

---

## §C 执行

按 C1（模板见 §E2）写新 SKILL.md → 拆 references（C2，每个带元信息头）→ 保留已有 references（C3）

---

## §D 验证

```bash
wc -l SKILL.md                                          # < 500
grep -c "Use when\|Do NOT use\|Delegate to\|Reads knowledge\|Done when" SKILL.md  # ≥ 5
grep -c "入口决策" SKILL.md                               # ≥ 1
# references 索引表中的每个文件都存在
```

---

## 参考文件

| 文件 | 何时加载 |
|------|----------|
| `references/scoring-checklist.md` | 执行 §A2 评分时 |
| `references/scoring-checklist.md` | 执行 §A2 评分时 |
| `references/design-philosophy.md` | 需要判断"硬 gate vs 信任判断"时——四学派对比与决策框架 |
| `~/.hermes/docs/hermes-skill-refactoring-spec-v1.md` | 需要完整规范时 |

> 本技能已开源
