# Hermes Skill 重构规范 v1.0

> 2026-06-13 · 消化自 Anthropic Skills 方法论 + Codex 架构审查 + 内部审计

---

## 一、核心原则

| # | 原则 | 含义 |
|---|------|------|
| P1 | **调度协议优先** | 技能不是"能力说明书"，而是"可调度、可委派、可验证的协议" |
| P2 | **入口即决策树** | 第一屏必须让 agent 判断"我面对的是哪类情况" |
| P3 | **Description 是触发器** | description 必须 pushy，列出触发词/场景/反触发 |
| P4 | **500 行硬上限** | SKILL.md 超 450 行即强制拆分。正文只留入口+决策+最小流程 |
| P5 | **脚本黑盒化** | 可确定执行的流程必须进 `scripts/`，正文只写调用方式 |
| P6 | **渐进披露** | 元数据(100tok)→正文(<500行)→resources(按需)。每层独立可用 |
| P7 | **迭代闭环** | 复杂技能必须有 eval/验证/复盘机制 |

---

## 二、强制骨架（每个 SKILL.md 顶部必须包含）

```markdown
## 协议层

| 字段 | 内容 |
|------|------|
| **Use when** | [触发条件：用户说了什么、任务是什么类型、系统处于什么状态] |
| **Do NOT use when** | [反触发：什么情况下不该用这个技能] |
| **Delegate to** | [委派给哪个助手 / null 表示花生酱自己执行] |
| **Reads knowledge** | [读写知识图谱的哪些节点] |
| **Done when** | [完成条件：什么情况下这个技能的任务算完成] |
```

### 示例（skill-radar）

```markdown
| **Use when** | 用户说"技能雷达""扫描外部技能""skills.sh""有什么新技能"；或 cron 周一触发 |
| **Do NOT use when** | 用户只是问某个具体技能怎么用（那是 skill-view 的事） |
| **Delegate to** | 苔姨 |
| **Reads knowledge** | 读取 skill-radar-baseline.md；写入 skills-ecosystem-overview.md |
| **Done when** | 周报已推送到 Telegram，且基线已更新 |
```

---

## 三、入口决策树规范

每个技能的 SKILL.md 正文必须以决策树开头（协议层之后）。格式：

```markdown
## 入口决策

你面对的是哪种情况？

1. **[场景A]** → 执行 [对应流程]，跳转到 §A
2. **[场景B]** → 执行 [对应流程]，跳转到 §B
3. **[场景C]** → 加载 `references/xxx.md`，然后...
4. **不确定** → [默认行为]
```

---

## 四、内容分层规则

| 层级 | 放什么 | 不放什么 |
|------|--------|----------|
| **SKILL.md 正文** | 协议层 + 入口决策 + 最小执行流程 + references 索引 | 详细步骤、长代码示例、历史 changelog、领域知识细节 |
| **references/** | 领域知识、详细流程、API 文档、平台差异、长代码示例 | 可执行脚本逻辑 |
| **scripts/** | 可独立运行的黑盒脚本（`--help` 自说明） | 需要 agent 推理判断的内容 |
| **assets/** | 模板、图片、数据文件、schema | 执行逻辑 |

---

## 五、Description 规范

```yaml
description: [做什么] + [什么时候用]。必须包含触发关键词。
```

**好例子：**
```yaml
description: >
  扫描 skills.sh 和 GitHub 生态，发现可消化的新技能，产出周报。
  当用户提到"技能雷达""外部技能""skills.sh""有什么新技能""扫描技能生态"
  或 cron 定时触发时使用。TTL 3分钟以内。
```

**坏例子：**
```yaml
description: 苔姨专用 · 外部技能雷达
```

---

## 六、脚本黑盒规范

1. 每个脚本必须有 `--help`，输出参数说明和示例
2. SKILL.md 中只写调用方式，不写源码
3. 脚本用 Python（优先）或 Bash
4. 脚本放在 `scripts/` 目录下

**SKILL.md 中的写法：**
```markdown
### 扫描执行

```bash
python scripts/skill_radar_scan.py --categories all --since 7d --baseline ~/.hermes/memory/skill-radar-baseline.md --output /tmp/radar-report.md
```

详见 `--help`。
```

---

## 七、迭代验证规范

复杂技能（评分 ≥ 3 的 skill-radar 类、≥ 5 的 coordinator-workflow 类）必须包含：

```markdown
## 验证与复盘

- **单次验证**：[怎么确认这次执行成功了]
- **定期复盘**：[cron 或触发条件，怎么评估技能质量]
- **改进记录**：[引用 references/changelog.md]
```

---

## 八、重构优先级（基于 2026-06-13 审计）

| 优先级 | 技能 | 核心问题 | 目标 |
|--------|------|----------|------|
| P0 | hermes-agent | 922行，无决策树 | 拆分入口+references |
| P1 | peanutbutter | 608行，上下文污染 | 瘦身到350行+决策树 |
| P2 | skill-radar | 无反触发/无黑盒脚本 | 脚本化+协议骨架 |
| P3 | official-document-drafter | 正文像标准手册 | 拆references+脚本 |
| P4 | coordinator-workflow | 已达可用，补最后20% | 优化description+入口 |

---

## 九、skill-radar 试点（2026-06-13）

作为第一个按本规范重构的技能。详见 `~/.hermes/profiles/gemini/skills/skill-radar/SKILL.md`（重构后）。

改动摘要：
- 新增协议层（5行骨架）
- 新增入口决策（首次基线/周报/临时搜索/异常降级）
- 新增黑盒脚本 `scripts/skill_radar_scan.py`
- 拆分领域细节到 `references/scoring-rules.md`
- Description 改为 pushy 风格
- 新增"值得消化评分"体系

---

## 十、v1.1 新增（2026-06-13 · Codex 设计）

### 10.1 Reference 元信息头

每个 `references/*.md` 文件顶部必须添加标准化元信息 YAML frontmatter：

```yaml
---
reference_id: cli-reference
title: Hermes CLI Reference
scope: 该 reference 覆盖的知识范围（一句话）
applies_to:
  - hermes-agent
  - hermes-debug
source_type: reference
staleness_risk: high
last_verified: 2026-06-13
owner_skill: hermes-agent
---
```

| 字段 | 类型 | 必填 | 说明 |
|---|---:|---:|---|
| `reference_id` | string | 是 | 稳定 ID，等于文件名去掉 `.md` |
| `title` | string | 是 | 人类可读标题 |
| `scope` | string | 是 | 覆盖的知识范围 |
| `applies_to` | string[] | 是 | 主要使用该 reference 的技能 |
| `source_type` | enum | 是 | 固定为 `reference` |
| `staleness_risk` | enum | 是 | `high` / `medium` / `low` |
| `last_verified` | date | 是 | 最近验证日期 `YYYY-MM-DD` |
| `owner_skill` | string | 是 | 负责维护的主技能 |

`staleness_risk` 分级：
- **high**：版本更新时极可能变化（CLI 命令、配置项、认证流程）
- **medium**：依赖外部服务行为（provider 可用性、平台支持）
- **low**：相对稳定的概念和流程（agent loop、commit 规范）

### 10.2 双向 Handoff 协议

每个技能在协议层之后、入口决策之前，新增一个 `§Handoff` 章节。

**与 `Delegate to` 的区别**：
- `Delegate to`：这个技能该派给哪个助手执行（委派）
- `Handoff`：这个技能解决不了时，该把用户交给哪个技能继续处理（接力）

格式不超过 5 行：

```markdown
## §Handoff
- Trigger: <当前技能无法继续处理的条件>
- Target: <目标技能>
- Context: <必须带过去的上下文>
```

三个标准实例：

**hermes-agent → coordinator-workflow**：
```markdown
## §Handoff
- Trigger: 用户目标涉及多技能编排、任务拆分、跨阶段交付或需要协调多个 Hermes 技能
- Target: coordinator-workflow
- Context: 用户原始目标、已确认的 Hermes 约束、当前技能已完成/未完成事项
```

**coordinator-workflow → hermes-agent**：
```markdown
## §Handoff
- Trigger: 编排过程中需要配置、修改或验证 Hermes agent 行为、CLI 使用、provider/model 选择
- Target: hermes-agent
- Context: 当前工作流阶段、分配给 agent 的具体任务、验收标准
```

**hermes-debug → hermes-agent**：
```markdown
## §Handoff
- Trigger: 问题不是故障排查，而是需要新增/重构 Hermes agent 能力或调整正常工作流
- Target: hermes-agent
- Context: 报错现象、已排除的原因、Hermes 版本/命令输出、用户真正想达成的目标
```

### 10.3 错误答案防线

每个涉及外部知识的 reference 或技能，必须包含「常见错误答案」小节，拦截模型高频错误回答。

格式：

```markdown
## 常见错误答案

### 错误：<错误答案或错误做法>
- Why wrong: <为什么错>
- Correct: <正确答案>
- Check before answering: <回答前必须核对的依据>
```

**与 pitfalls 的区别**：
- Pitfalls：使用这个技能时容易踩的坑（操作层面）
- 错误答案防线：模型在回答相关问题时容易给出的错误答案（知识层面）

三个标准实例（hermes-agent）：

```markdown
### 错误：把 hermes-agent 用作通用调试技能
- Why wrong: hermes-agent 负责能力构建/配置；故障定位应先由 hermes-debug 处理
- Correct: 报错/失败/异常输出/认证失败时，优先交给 hermes-debug
- Check before answering: 用户是在「构建 agent」还是「排查失败」

### 错误：随意给模型名添加 provider 前缀
- Why wrong: 错误前缀导致模型解析失败或选错 provider
- Correct: 按 `hermes model` 和 `cli-reference.md` 格式选择，不凭记忆拼接
- Check before answering: 核对 `references/cli-reference.md` 确认当前版本格式

### 错误：使用 `hermes login` 处理 Codex 认证
- Why wrong: `hermes login` 已废弃。应使用 `hermes auth` 管理凭证
- Correct: 认证用 `hermes auth`；provider 选 `hermes model`；初始化用 `hermes setup`
- Check before answering: 核对 CLI reference 确认命令未被废弃
```
