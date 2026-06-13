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

---

## 十一、v1.2 新增（2026-06-13 · 四方辩论裁决）

> 消化自：Anthropic（信任判断力）+ MiniMax（工程硬度）+ Codex（安全裕度+作者模型）+ Claude Opus（范式选择）

### 11.0 哲学立场

本规范的根基是**协作范式**，不是命令范式。

我们信任 agent 在运行时的判断力——决策树、协议层、Handoff、"不确定→查证"这些机制的存在前提就是对判断力的信任。但我们不天真到信任所有技能作者。所以：

- **信任给 agent**：任务理解、路径选择、审美判断、用户意图适配
- **不信任给系统层**：破坏性操作、真实性声明、外部副作用、安全边界、认证凭证

> *"当你们为某条规则争论该用绝对语气还是条件 gate 时，本质上是在问'我们信任运行时的 agent 吗'——如果答案是不信任，那问题不在规则措辞，在于你们选错了协作范式。"* — Claude Opus

### 11.1 系统级 Blocking Invariants

以下规则是**系统级铁律**，不写在单个 SKILL.md 里，而是由 coordinator-workflow 的 intake-layer 统一执行。技能作者无权覆盖。

| # | Invariant | 执行者 |
|---|-----------|--------|
| 1 | **真实性**：不得伪造执行结果。API 调用失败时必须报告失败，不得编造响应。 | coordinator |
| 2 | **破坏性操作**：删除文件/目录/数据前必须确认或备份。 | coordinator |
| 3 | **认证凭证**：缺少必要 API key 时必须停止，不得假装调用成功。 | coordinator |
| 4 | **外部副作用**：生产环境变更、外部服务调用、发送消息前必须检查目标。 | coordinator |
| 5 | **文件路径**：写入/覆盖文件前必须确认路径存在且可写。 | coordinator |
| 6 | **机器消费格式**：子代理间交付、自动化评测、CI/CD 报告必须符合 schema。 | 子代理协议 |
| 7 | **脚本执行**：来自技能的 `scripts/` 必须在确认来源后执行（不盲跑）。 | coordinator |
| 8 | **冲突回退**：两个技能给出的指令冲突时，以系统级 invariant 为准，上报花生酱。 | coordinator |

**反规则**：禁止将审美偏好、输出风格、流程习惯、句式模板写成 MUST。当所有规则都是 MUST，agent 就学会忽略 MUST。

### 11.2 Contextual Pre-flight Gates

Gate **不在技能里定义，而在 coordinator 路由时触发**。路由到某类任务 → 触发对应 gate。

| 任务类型 | 触发条件 | Gate 检查项 | 失败处理 |
|----------|----------|------------|----------|
| 图像生成 | 路由到 `peanutbutter` 或调用 `image_generate` | provider 配置、模型可用性 | 提示用户配置 / 降级 curl |
| API 调用 | 路由到任何含外部 API 的技能 | key 存在、endpoint 可达、quota 余量 | 停止 / 切换 provider |
| 文件操作 | 路由到读写/删除文件任务 | 路径存在、权限可写、覆盖风险 | 询问确认 / 备份 |
| 音视频处理 | 路由到含 ffmpeg/媒体处理 | ffmpeg 可用、输入文件存在 | 提示安装 / 跳过 |
| 代码执行 | 路由到 `terminal` / `execute_code` | 工作目录存在、包管理器可识别 | 降级为纯分析 |
| 部署操作 | 路由到 `deployment` 相关 | 目标环境可达、回滚方案存在 | 停止 / 要求确认 |

**关键原则**：gate 是条件化的——只在相关任务触发时才检查。不存在"所有任务第一步都检查 venv/API key/ffmpeg"的全局 gate。

### 11.3 状态缓存（State Caching）

为 agent 提供带失效机制的短期工作记忆，减少重复探索。是系统基础设施，所有技能可调用。

**缓存条目格式**：

```json
{
  "key": "project.test_command",
  "value": "npm test",
  "source": "package.json scripts",
  "verified_at": "2026-06-13T10:20:00Z",
  "valid_until": "session",
  "invalidates_when": ["package.json changes", "working directory changes"],
  "confidence": 0.94
}
```

**失效条件**（满足任一即失效）：
- TTL 过期
- 来源文件 hash 变化
- 依赖版本变化
- 会话切换
- 用户显式否定

**不允许**：无来源缓存、永久缓存、跨会话默认复用。

### 11.4 Output Contract（仅机器交接）

不强加 XML 格式。子代理间交付和自动化评测可使用结构化合约：

```json
{
  "status": "success|failure|partial",
  "summary": "一句话",
  "artifacts": ["文件路径列表"],
  "verification": "如何验证"
}
```

用户-facing 回答不适用此格式。Done when 字段仍然是主要的完成定义。

### 11.5 Concurrency Marking（轻量标注）

技能可在执行步骤中标注并行/串行依赖：

```text
∥ Parallel:
  - 读取 config.yaml
  - 读取 .env
  - 搜索文档

→ Sequential:
  - 安装依赖 only after 确认包管理器
  - 运行测试 only after 安装完成
```

不强制。coordinator-workflow 已有隐式并行调度能力。

### 11.6 明确拒绝清单

以下 MiniMax 模式经四方辩论后**不予吸收**：

| 拒绝 | 理由 |
|------|------|
| Universal Mandatory Compliance | 规则通胀摧毁 MUST 的可信度（Claude Opus 警告） |
| Localization Layer 进核心 | 工具适配层，不是 agent 核心哲学 |
| 全局 Pre-flight Gate | 无脑检查污染所有任务 |
| 刚性 XML Output Contract 用于用户回答 | 格式主义，阅读体验差 |

---

*本规范将持续演进。每次吸收外部方法论时，先问："这是增强 agent 判断力，还是替代 agent 判断力？"——如果是后者，大概率不该要。*
