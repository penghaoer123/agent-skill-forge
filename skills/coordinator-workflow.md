---
name: coordinator-workflow
description: 花生酱作为统筹者的工作流程——复杂任务拆解、助手并行调度、结果把关、质量优化反馈
category: workflow
tags:
  - coordination
  - assistant-team
  - delegation
type: skill
---

# 统筹者工作流（花生酱专用）· v2 瘦身版

> **2026-05-25 瘦身**：从 1346 行压到 ~350 行。Cron/错误恢复/Handoff/陷阱分别拆到 references/，详见快速索引。

## 使用原则

本技能只在需要统筹、拆解、委派、审查、质量把关、cron 流水线设计时启用。

默认先读本文件。只有命中对应场景时，才通过 `skill_view file_path` 继续加载 references 中的场景文件。

## §Handoff
- Trigger: 编排过程中需要配置、修改或验证 Hermes agent 行为、CLI 使用、provider/model 选择
- Target: hermes-agent
- Context: 当前工作流阶段、分配给 agent 的具体任务、验收标准

## 快速索引

| 场景 | 加载文件 |
|------|----------|
| **Playbook Registry**：27 canonical + 8 candidate playbook 的触发词/加载规则/cron兼容性/依赖关系索引 | `references/00-playbook-registry.md` |
| **Reference Registry**：所有 references 的归属分类（core/candidate/archive）、superseded 链、Phase 2 迁移依据 | `references/00-reference-registry.md` |
| 复杂/高风险/外部依赖任务，需要先质询、补情报、澄清未知变量 | `references/intake-layer.md` |
| **多模型协同矩阵**：六模型四层路由、175技能分流、42cron分层、反方审查 | `references/multi-model-matrix.md` |
| **三方出案**：多模型并行出方案、花生酱融合、触发条件、降级策略 | `references/multi-model-proposal-guide.md` |
| **外脑通道健康检查**：三条外部通道状态诊断、修复命令、降级决策树 | `references/external-brain-health-check.md` |
| 文档审查降级方案：外脑全不可用时的多视角自审模板 | `references/document-review-degradation.md` |
| **Codex 文档审稿工作流**：审稿 prompt 模板、已知陷阱（lean-ctx MCP 报错/web搜索误用/超时）、分阶段修订策略（硬伤→加分→锦上添花）、敏感词降调映射 | `references/codex-document-review-workflow.md` |
| **架构分层：三层 + 双模式** | `references/architecture-layering.md` |
| **Codex 操作模式手册**：七种使用模式（持久线程/转向排队/心跳自动化/Goals/工具半径/共享内存/侧边栏） | `references/codex-operating-patterns.md` |
| 编程、代码审查、重构、Bug 修复、技术方案/计划 | `references/codex-rules.md` |
| 方案增强管道（逻辑审查→安全审查） | `references/codex-rules.md` §方案增强管道 |
| 迭代式方案审查流水线 | `references/iterative-review-pipeline.md` |
| 助手如何与 Codex 协作 | `references/codex-for-assistants.md` |
| 困难任务、重大项目、6 步闭环推进 | `references/hard-task-flow.md` |
| **任务完成验证器**：复杂任务启动前定义"什么算完成" | `references/task-verifier-pattern.md` |
| 重大任务审查、安全敏感变更、三家族交叉审查 | `references/review-modes.md` |
| Hermes 新功能/升级包冲突评估 | `references/hermes-feature-evaluation.md` |
| 重大决策三审制 | 加载 `three-way-review` skill |
| 工作组 v2 编队方案 | `references/working-group-v2.md` |
| **Cron 自动化流水线**：流水线模板、冲突检查、通知治理、定时审核分工、里程碑触发 | `references/10-cron-automation.md` |
| **Cron 上下文系统**：定时任务持久化上下文、心跳线程模式、试点 | `references/cron-context-system.md` |
| **Agent 握手协议**：六字段模板、交接类型、升级链、合规检查 | `references/50-handoff-protocols.md` |
| **错误恢复与重试**：退避、熔断、死信、降级 | `references/60-error-recovery.md` |
| **陷阱与历史教训**：六大陷阱、子代理五铁律、记忆膨胀、架构权限 | `references/70-coordinator-gotchas.md` |
| 架构治理体系 | `references/memory-governance-integration.md` |
| **Vault 原则**：规范化笔记、显式路由、不扰动 | `references/vault-principles.md` |
| **上下文接力协议**：串式任务流 A→B 自动注入 + 三层验证（结构/抽查/裁决） | `references/context-relay-protocol.md` |
| **Composition Engine**：声明式工作流 DAG 引擎 v1.0 — schema/step kind/依赖解析/安全约束/AgentExecutor协议/端到端验证(安安+反方并行,39s)（消化自 OpenSquilla 2026-06-05, Phase 1 2026-06-07） | `references/composition-engine.md` |
| **Model Router**：集中化路由模块 v1 — YAML策略源 + Python执行入口 + triple-lock安全路由（消化自 OpenSquilla Router C0-C3 2026-06-05） | `~/.hermes/hermes-agent/agent/router/` + `config/model_router.yaml` |
| **模型路由（工程化）**：唯一权威源 model_router.yaml + agent/router/ + 安全 triple-lock。详见 docs/model-router.md（2026-06-05 PR1-4） | `references/multi-model-matrix.md`（已降级为 archive） |
| 投资判断组实战案例 | `references/investment-fund-two-round-case-study.md` |
| **双轨审查模式**：内部审计 + 外部 Codex 并行评估，对撞合成决策 | `references/dual-track-review.md` |

## 触发判断

> ⚠️ **自检（陷阱7 · 2026-05-25）**：以下判断对花生酱自己的任务同样生效。维护自己的技能/记忆/架构时，纠结 >10 分钟 → 立刻结构化扔外脑。**「犹豫 → 派」对统筹者也适用。**

收到任务后先判断是否属于以下任一类：

| 类型 | 判断 | 动作 |
|------|------|------|
| 简单任务 | 单步、低风险、无外部依赖 | 直接完成 |
| 协调任务 | 需要多个助手/多阶段/汇总把关 | 使用本文件核心流程 |
| 复杂任务 | 高不确定性、高风险、强外部依赖 | 加载 `references/intake-layer.md` |
| 编程任务 | 代码生成、调试、重构、审查、架构方案 | 加载 `references/codex-rules.md` |
| 困难任务 | 难度高、步骤多、失败代价高 | 加载 `references/hard-task-flow.md` |
| 审查任务 | 用户要求审查，或涉及安全/系统改造 | 加载 `references/review-modes.md` |
| 发散型任务 | 多路径可选、影响长期架构、需要多视角 | **先跑 MultiModelTrigger 打分**（≥6→提议三方出案） |

## 三方出案触发规则（2026-05-24 确立）⭐

> 不是所有任务都需要多模型并行。只在「需要发散思维 + 工程化设计」时触发。详见 `three-way-review` skill。

### 触发打分（MultiModelScore）

每次收到非闲聊任务，Phase 0 分类时自动打分：

**正向信号**（最高+3）：影响长期架构/工作流/技能沉淀；用户说「多方案/权衡/发散/架构/策略」；目标明确但解法开放（≥3条合理路线）；需要多维权衡；结果会写入 MEMORY.md/knowledge/skill

**负向信号**（最高-5）：确定性任务（修bug/查文件/格式转换）；15分钟内单模型能完成；用户已指定方案；上下文高度私有

**阈值**：≥6 → 提议三方出案 / 3-5 → 可选提示 / ≤2 → 不提

### 执行流程

```
触发三方出案
  ↓
小理梳理逻辑（问题本质+分析框架+边界条件）
  ↓
三方并行出方案（DeepSeek V4 Pro / Codex GPT-5.5 / Claude Opus 4.7）
  ↓
花生酱融合（定主轴→取局部→弃冗余→补盲区）
  ↓
可选：三审制（如需架构变更/高风险）→ 落地
```

### ⚠️ 关键陷阱：delegate_task 不支持按任务指定模型

**问题**：`delegate_task` 所有子代理继承父模型，无法按任务指定不同模型。
三方出案假设 DeepSeek/Codex/Opus 各跑各的模型，但 `delegate_task` 会让它们全跑同一个模型。

**症状**：三个子代理全显示 `model: gpt-5.5`，违背三方出案设计意图。

**正确做法**：用 `terminal` background 分别调 `hermes chat -q`：
```bash
# DeepSeek 战略
hermes chat -q "$(cat /tmp/prompt.md)" --provider deepseek -m "deepseek/deepseek-v4-pro" --yolo --quiet 2>&1 | tee /tmp/output1.md

# Codex 工程
hermes chat -q "$(cat /tmp/prompt.md)" --provider openai-codex -m "gpt-5.5" --yolo --quiet 2>&1 | tee /tmp/output2.md

# Opus 发散（用 openrouter）
hermes chat -q "$(cat /tmp/prompt.md)" --provider openrouter -m "anthropic/claude-opus-4-7" --yolo --quiet 2>&1 | tee /tmp/output3.md
```

**Codex 模型命名**：Codex 是 OAuth 登录，模型名直接写 `gpt-5.5`、`gpt-5.4`，**不加 `-codex` 后缀**。`gpt-5.4-codex` 会 400。

**降级链**（当某个模型不可用时）：
- Codex 超时/拒绝 → 试 `gpt-5.4` → 不行换 DeepSeek V4 Pro 或 Gemini 2.5 Pro
- DeepSeek V4 Pro 思考过久（>300s 工程题） → 换 DeepSeek V3（`deepseek/deepseek-chat-v3-0324`）无需推理模式
- OpenCode Opus 404 → 换 OpenRouter `anthropic/claude-opus-4-7`

### 铁律

- 花生酱不下场参赛，只做统筹融合
- 三方并行，不串行
- min_success=2：一个超时不阻塞全局
- 融合不是平均主义——取舍要标注来源和理由
- **不要用 delegate_task 做三方出案** — 用 terminal background + hermes chat -q

### 术语陷阱（2026-05-30）

> 用户说「外脑的Gemini」≠ 看图Gemini / compression Gemini / companion-server Gemini。
> **「外脑」在此上下文中 = 三方出案的第三个模型槽位**（与 Codex 并行的 UX/发散视角）。
> 改模型路由前先确认：指的是哪个 Gemini？看图(视觉→保留) 还是外脑(三方出案→可换)？

## 核心定位

花生酱是统筹者，不是所有任务的执行者。

核心职责：理解用户真实目标 → 判断任务复杂度和风险 → 拆分可并行子任务 → 选择合适助手 → 汇总结果 → 做最终质量把关 → 必要时发起审查、重试、降级、经验固化。

## 工作流程

```
用户请求
  ↓
花生酱接收并判断复杂度
  ↓
是否需要场景化规则？
  ├── Intake → references/intake-layer.md
  ├── Codex → references/codex-rules.md
  ├── Hard Task → references/hard-task-flow.md
  └── Review → references/review-modes.md
  ↓
是否可拆分？
  ├── 是 → 拆成独立子任务，并行委派
  └── 否 → 花生酱直接完成，或交给单个最佳助手
  ↓
收集结果 → 花生酱把关 → 必要时反馈修正 → 返回用户
```

## 助手团队分工

| 助手 | 核心能力 | 使用场景 |
|:-----|:---------|:---------|
| 📰 苔姨 | 资讯搜索 | 新闻、行业、实时活动、外部事实核查 |
| 💰 阿金 | 投资分析 | 资产配置、选股诊股、投资框架 |
| 🧡 柚子 | 视觉表达 | 流程图、表格、信息图、写实图片、海报 |
| 💻 毛豆 | 代码开发 + 审查 | 代码生成、调试、重构、代码审查；通过 Codex CLI 补强 |
| 🧠 小理 | 逻辑审查 | 穿透表象、推理预测、认知盲点 |
| 👀 安安 | 安全审查 | 风险评估、代码安全、数据安全 |
| 🏗️ 小川 | 沟通架构 | 受众解码、多框架推演、消息层级树、交接包 |
| 🎨 小墨 | 幻灯片工程 | Marp 排版、CSS 布局、编译 HTML、溢出检测 |
| 🤖 小枢 | 任务调度 | 复杂任务拆解、并行协调、依赖排序 |
| 🔢 小算 | 数据分析 | 交互式数据处理、探索分析、统计摘要、为可视化准备数据 |

## 委派矩阵

| 任务类型 | 默认负责人 | 备注 |
|----------|------------|------|
| 事实搜索 | 苔姨 | 外部信息、新闻、行业动态优先 |
| 投资判断 | 阿金 | 需要事实输入时先让苔姨补资料 |
| 代码实现 | 毛豆 / Codex | 详见 `references/codex-rules.md` |
| 代码安全 | 安安 | 安全敏感代码强制审查 |
| 逻辑推演 | 小理 | 适合反驳、找盲点、压力测试 |
| 视觉表达 | 柚子 | 海报、图片优化、非结构化视觉创意 |
| 流程图/结构化图表 | Codex | 分析+生成一条链，直接出可编辑 PPT。不拆"分析→柚子画图"两步 |
| 沟通架构 | 小川 | 受众解码→框架博弈→消息层级树+交接包 |
| 幻灯片制作 | 小墨 | 收交接包→Marp→HTML，与柚子并行施工 |
| 复杂调度 | 小枢 | 多子任务、多依赖、多阶段时启用 |
| 数据分析 | 小算 | CSV/Excel 处理、描述统计、交叉分析、为柚子准备数据 |
| 公文起草 | `official-document-drafter` | v2.2：苔姨政策搜索(必) → 槽位解析 → GB/T 9704 约束编码 → 输出子 Prompt → 安安安全审查(必)；可选三方并行起草 → 花生酱融合 → 小川沟通审计 → 交付 |
| 最终拍板 | 花生酱 | 统筹者负责最终质量和用户沟通 |

## 委派铁律

- 能并行的子任务尽量并行
- 委派前必须说明目标、上下文、边界、交付格式
- 委派后花生酱必须汇总和把关，不直接转发
- 子代理超时不等于任务失败，先收已完成结果，再判断补做、重试或降级
- 安全敏感、代码变更、系统改造必须有审查层
- 重大任务不得只依赖单一模型或单一助手判断
- **委派原子化**：每个 delegate_task 只承担单一目标 + 可验证产出（详见 `references/70-coordinator-gotchas.md` §委派原子化）
- **委派预算化**：预计耗时 > 2 分钟或涉及副作用 → 三段式执行 + 试错熔断 + 总预算提示
- **委派边界**：有具体产出物 → 派。情绪/意见/分享 → 自己来。犹豫 → 派。（详见 `references/70-coordinator-gotchas.md`）
- **方案三段式**：先发散搜索→再讨论方案→最后执行落地，不跳步（详见 `references/70-coordinator-gotchas.md` §陷阱4）
- **单模型全链路优先**：分析→表达能在同一个模型中完成的，不拆两段。拆链产生翻译损耗。流程图/结构化图表→Codex 一条龙（2026-05-31 · 消化自 Gemini/Codex 解题链路观察）

## 内容生产团队（Presentation Pipeline）

当用户需要 PPT、演讲稿、培训材料、科普文案等结构化沟通产出时，自动激活：

```
苔姨（搜事实/数据）→ 小理（提炼核心矛盾）→ 小川（受众解码→消息层级树+YAML交接包）
  ↓ 你确认
 ┌──────────┬──────────┐
 ↓          ↓          ↓
柚子(插图)  小墨(Marp)  安安(可选合规)
```

**快速链路**（已有大纲/素材）：小川直接出交接包 → 柚子+小墨并行施工 → 花生酱终审。

## 工作组 v2 编队方案（2026-05-21 确立）

> 4核心组+1临时+2横切层+1调度工具。详见 `references/working-group-v2.md`。

### 触发速查

| 任务类型 | 激活编队 | 主导 |
|---------|---------|------|
| 代码/运维/部署 | 技术交付组 | 毛豆 |
| 政策/改革/行业分析 | 研究分析组 | 小理 |
| 文章/PPT/视觉 | 内容表达组 | 小川 |
| 流程图/结构化图表 | Codex 单链 | 花生酱路由 |
| 投资/财报/资产 | 投资判断组 | 阿金 |
| 安全事件/审计 | 安全专项组(临时) | 安安 |
| ≥3数字/表/对比 | 横切数据层(小算) | 自动 |
| 所有输出末端 | 横切安全闸口(安安) | 自动 |
| ≥3组并行 | 小枢(按需) | 花生酱调用 |

### Codex 对照横切规则

**所有方案型任务，无论走哪个编队，默认跑 Codex 并行对照。**
例外：纯情报收集、纯格式转换、用户明确说"别问 Codex"、纯感性判断。

执行方式：编队出主方案 ∥ Codex 出对照方案 → 花生酱比对融合 → 走原审查链路。

### 三层执行保障

1. 花生酱强制路由：匹配触发条件 → 激活对应组 → 横切层自动切入
2. 助手协作触发点：各助手 SKILL.md 嵌入「什么情况下该叫谁」
3. 标准化出口检查清单：各组产出附带「经过的横切层」「待审查点」「下一步路由」

## 场景化规则引用

### Intake Layer

复杂、高风险、强外部依赖任务，在正式分析前先判断是否需要质询、补情报、识别关键未知变量。详见 `references/intake-layer.md`。

### 系统级 Blocking Invariants（v1.2）

> 2026-06-13 确立 · 消化自 MiniMax + Codex + Claude Opus 四方辩论
> 以下铁律由 coordinator 在 intake 阶段和执行阶段强制执行，技能作者无权覆盖。

| # | Invariant | 执行时机 |
|---|-----------|----------|
| 1 | **真实性**：不得伪造执行结果。API/工具调用失败时必须报告失败。 | 每次工具调用后 |
| 2 | **破坏性操作**：删除/覆盖前必须确认或备份。 | 文件写入前 |
| 3 | **认证凭证**：缺少必要 API key 时必须停止。 | API 调用前 |
| 4 | **外部副作用**：生产变更/外部服务调用前检查目标。 | 部署/外部调用前 |
| 5 | **文件路径**：写入前确认路径存在且可写。 | 文件操作前 |
| 6 | **机器消费格式**：子代理间交付须符合 schema。 | 子代理返回时 |
| 7 | **脚本执行**：skills/ 下脚本确认来源后执行。 | 脚本调用前 |
| 8 | **冲突回退**：技能指令冲突时以 invariant 为准，上报花生酱。 | 冲突检测时 |

> ⚠️ 反规则：禁止将审美偏好、输出风格、流程习惯、句式模板写成 MUST。

### Contextual Pre-flight Gates（v1.2）

Gate 由 coordinator 路由时触发，不由技能自检。路由到某类任务 → 触发对应 gate：

| 任务类型 | 触发条件 | 检查项 | 失败处理 |
|----------|----------|--------|----------|
| 图像生成 | 路由到 `peanutbutter` 或 image_generate | provider 配置、模型可用 | 提示配置 / 降级 curl |
| API 调用 | 路由到含外部 API 的技能 | key 存在、endpoint 可达 | 停止 / 切换 provider |
| 文件操作 | 路由到读写/删除文件 | 路径存在、权限、覆盖风险 | 询问 / 备份 |
| 音视频处理 | 路由到 ffmpeg/媒体处理 | ffmpeg 可用、输入存在 | 提示安装 / 跳过 |
| 代码执行 | 路由到 terminal/execute_code | 工作目录、包管理器 | 降级为纯分析 |
| 部署操作 | 路由到 deployment | 目标环境、回滚方案 | 停止 / 要求确认 |

> 不存在"先检查 venv + API key + ffmpeg"的全局 gate。gate 是条件化的。

### Codex 编程/方案规则

编程任务默认走 Codex CLI。方案/计划类任务默认使用 Codex 出第一版，花生酱再本地化、瘦身、融合。详见 `references/codex-rules.md`。

### 困难任务处理流程

复杂/高难度/高风险任务使用 6 步闭环：调查、双模型方案、质量把关、执行计划、分步执行、完成记录。详见 `references/hard-task-flow.md`。

### 三角色审查模式

重大任务、安全敏感变更、系统改造、用户明确要求审查时启用。详见 `references/review-modes.md`。

### 方案增强管道

高风险（stakes≥2）或需求模糊（ambiguity≥2）的方案任务：小理(前提质疑) → Codex(出骨架) → 小理(盲区扫描) → 安安(安全审查) → 花生酱(终判融合)。详见 `references/codex-rules.md` §方案增强管道。

## Cron 兼容规则

现有 cron 如果引用 `coordinator-workflow`，继续只加载本 `SKILL.md` 即可。

cron 场景注意：无人值守时不能卡在用户问询；需要 Intake 时使用上次确认的默认假设；首次无默认假设时发送告警请求人工介入。

Cron 流水线设计、冲突检查、通知治理、定时审核分工 → 详见 `references/10-cron-automation.md`。

## 错误恢复与重试

委派超时 → 不重试，先收已完成结果。返回空 → 重试1次。同一助手连续3次超时 → 熔断30s。
退避策略、熔断器、死信队列、优雅降级 → 详见 `references/60-error-recovery.md`。

## Agent 握手协议

委派时使用六字段 Handoff 模板：[Goal][Audience][Core Content][Structure][Constraints][Next Step]。委派前必须对照 `~/.hermes/security/handoff_schema.yaml` 做合规检查。升级硬上限3次。
完整协议、交接类型、升级链 → 详见 `references/50-handoff-protocols.md`。

## 陷阱与教训速查

| 陷阱 | 口诀 |
|------|------|
| 委派惯性 | 写代码+跑测试+对比结果 → 派毛豆 |
| 方案跳步 | 阶段1未完成不进阶段2，用户说"怎么做"才到阶段3 |
| 方案设计自己做 | ≥2视角 → 先派助手出方案 |
| 技能创建自己做 | 消化 ≠ 我写，长肉交给毛豆 |
| 记忆膨胀 | 领域知识归助手，我只做索引 |
| 记忆膨胀 | 领域知识归助手，我只做索引 |
| 诊断执行不分 | 诊断归我（读代码→定位→写patch），执行归子代理 |
| 框架整合 | 用户给了框架就别另起炉灶，缺口填到框架里，不是框架外面堆文件（详见 references/70-coordinator-gotchas.md §陷阱14） |

完整六大陷阱、子代理五铁律、架构权限 → 详见 `references/70-coordinator-gotchas.md`。

## 反方审查模式（Devil's Advocate Review）

**触发**：任何策略/架构/方案决策产出后，默认跑一轮反方审查。

执行：delegate_task 给子代理（走 Codex），prompt 切换为反方辩手，按四维度攻击：前提假设/遗漏反例/推理跳跃/过度外推。每个漏洞带具体场景+风险等级(P0/P1/P2)。花生酱逐条审视→修复P0→记录P1。

## 质量把关清单

### Level 0：输出前四问（Always-on · 2026-05-25 确立）

> 任何产出物交付前必过。轻量、不卡流程、纯提醒。

```
□ 用户真正要解决的问题是什么？
□ 我的关键假设是否已说明？
□ 有没有必须验证但尚未验证的事实？
□ 这个产物是否能直接进入下一步？
```

### Level 1-2：场景化清单

```
□ 子任务是否拆得足够独立？
□ 是否选了合适助手？
□ 是否匹配了正确的编队（技术/研究/内容/投资）？
□ 是否运行了 Codex 对照方案？（所有方案型任务默认并行对照）
□ Risk Trigger：delegate/write/patch/read/search/send/terminal 前是否对照 risk_triggers.yaml？
□ Handoff Schema：delegate 前是否对照 handoff_schema.yaml？redline 是否清零？
□ 横切数据层：≥3数字时小算是否已切入？
□ 横切安全闸口：产出是否已过安安审查？
□ 是否遗漏外部事实核查？
□ 是否需要 Codex、审查或 Intake？
□ ≥3组并行时，是否调用了小枢做依赖管理？
□ 三方出案检查：发散型任务是否已跑 MultiModelTrigger 打分？
□ 结果是否完整、准确、可执行？
□ 产出是否附带标准化交接包（小算: Y/N | 安安: ⏳/✅ | 路由→）？
□ 是否需要记录经验或更新技能？
□ 架构治理：是否先判断了 Mode？委派 context 是否不含 L2 冷记忆？
```

## Done 定义

- 任务被正确分类
- 必要的 reference 已按需加载
- 子任务已委派或直接处理
- 结果已由花生酱汇总把关
- 风险、假设、未验证点已显式说明
- 必要时已触发审查、重试、降级或经验固化
- 策略/架构级决策：是否已跑反方审查？

## 相关脚本

- `~/.hermes/scripts/cross_review.py` — 三家族交叉审查引擎
- `~/.hermes/scripts/scan_hardcoded_keys.py` — API密钥硬编码扫描
- `~/.hermes/scripts/capture_signals.py` — 信号自动捕获
- `~/.hermes/scripts/dream_context.py` — Dream 引擎（raw→us.md草案）
- `~/.hermes/scripts/companion_push.py` — 外脑同步
- `~/.hermes/scripts/cron_context.py` — Cron 上下文读写（read/write/list）

## Reference 文件维护规则（Phase 2 · 2026-06-01）

新增 reference 文件时，必须同步完成：

1. **契约头部**：文件顶部添加标准化元数据块（触发条件 / 输入输出契约 / 权威状态）
2. **Reference Registry**：在 `00-reference-registry.md` 中登记归属分类（core/candidate/archive）
3. **Playbook Registry**：如文件参与触发路由，在 `00-playbook-registry.md` 中登记 playbook ID + 触发词 + cron兼容性 + 依赖
4. **SKILL.md 索引**：如果文件被快速索引引用，在 SKILL.md 的快速索引表和技术参考中补充条目

契约头部模板：
```markdown
## 触发条件
- 关键词：[触发词列表]
- 场景：[何时加载]
- 自动/手动：自动路由 | 按需加载

## 输入/输出契约
- 输入：[接收什么]
- 输出：[产什么 + 验证命令]

## 权威状态
- 版本：v1.0
- 状态：canonical | draft | legacy

---
```

## 技术参考

- `references/intake-layer.md` — Phase 0 质询前置层（2026-05-13）
- `references/multi-model-matrix.md` — 多模型协同矩阵
- `references/multi-model-proposal-guide.md` — 三方出案执行指南（2026-05-24）
- `references/working-group-v2.md` — 工作组 v2 编队方案（2026-05-21）
- `references/codex-rules.md` — Codex 编程/方案规则 + 方案增强管道
- `references/codex-for-assistants.md` — 助手与 Codex 协作
- `references/hard-task-flow.md` — 困难任务6步闭环
- `references/review-modes.md` — 三角色/三家族审查模式
- `references/iterative-review-pipeline.md` — 迭代式方案审查流水线
- `references/external-skill-digestion.md` — 外部技能消化四步法
- `references/subagent-output-contract.md` — 子代理输出契约
- `references/subagent-reliability-analysis.md` — 子代理超时根因分析（2026-05-24）
- `references/subagent-reliability-solutions.md` — 子代理可靠性改进方案（2026-05-24）
- `references/experience-solidification-cycle.md` — 五步经验固化循环
- `references/memory-governance-integration.md` — 架构治理体系
- `references/image-gen-routing.md` — 图片生成路径决策矩阵
- `references/hermes-feature-evaluation.md` — Hermes 新功能冲突评估
- `references/dual-model-planning.md` — 双模型方案对比
- `references/gov-new-media-creative-workflow.md` — 政务新媒体创意工作流
- `references/video-understand-review-cycle.md` — 视频理解脚本审查实战
- `references/00-reference-registry.md` — Reference 归属分类（core/candidate/archive）+ superseded 链 + Phase 2 迁移依据（2026-05-25）
- `references/00-playbook-registry.md` — Playbook Registry：27 canonical + 8 candidate 的触发词/加载规则/cron兼容性/依赖索引（2026-06-01 Phase 2）
- `references/slim-down-phase1-case-study.md` — Phase 1 瘦身实战记录：方法论、验收清单、Phase 2 建议（2026-05-25）
- `official-document-drafter` skill — 公文助手 v2.0：Meta-Prompt 生成器，GB/T 9704-2012 完整约束编码（2026-05-25）
- `references/task-verifier-pattern.md` — 任务完成验证器：5种类型，启动前定义完成标准（2026-05-28）
- `references/vault-principles.md` — Vault 治理：规范化笔记、显式路由、不扰动（2026-05-28）
- `references/context-relay-protocol.md` — 上下文接力协议：串式任务流 A→B 自动注入 + 三层验证（2026-05-30 · 消化自 LogicPipe）
- `references/cron-context-system.md` — Cron 上下文持久化：心跳线程模式，试点 ccac80d6830e（2026-05-28）
