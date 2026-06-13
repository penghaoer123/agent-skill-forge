---
name: skill-radar
description: >
  扫描 skills.sh 和 GitHub 生态，发现可消化的新技能，产出周报供花生酱筛选。
  当用户提到"技能雷达""外部技能""skills.sh""有什么新技能""扫描技能生态""外部技能周报"、
  或 cron 定时触发、或花生酱问"最近生态有什么值得看的"时使用。
  也支持临时手动扫描（--scoring strict 提高阈值快速出结果）。
  苔姨专用。TTL 3 分钟以内。
category: dev-tools
assistant_name: 苔姨
tags:
  - skill-discovery
  - radar
  - external-skills
type: skill
---

# 外部技能雷达 · v2

> 2026-06-13 重构：新增协议层 + 入口决策 + 黑盒脚本 + 消化评分体系。规范依据：`hermes-skill-refactoring-spec-v1.md`

## 协议层

| 字段 | 内容 |
|------|------|
| **Use when** | 用户说"技能雷达""扫描外部技能""skills.sh""有什么新技能"；或 cron 周一 09:00 触发；或花生酱问"最近生态有什么值得看的" |
| **Do NOT use when** | 用户只是问某个具体技能怎么用（那是 `skill-view` 的事）；用户要自己创建一个新技能（那是 `skill-creator` 的事） |
| **Delegate to** | 苔姨 |
| **Reads knowledge** | 读取 `~/.hermes/memory/skill-radar-baseline.md`（基线）；写入 `~/.hermes/memory/skill-radar-baseline.md`（更新基线） |
| **Done when** | 周报已通过 send_message 推送到 Telegram，且基线文件已更新 |

## 入口决策

你面对的是哪种情况？

1. **首次运行（无基线）** → 建立基线。扫描 → 生成全量列表 → 保存基线。不推周报（无对比意义）。
2. **例行周报（cron 周一触发）** → 完整扫描 → 脚本处理（去重+评分+对比） → 推 Telegram。跳转到 §扫描执行。
3. **临时手动扫描** → 同例行周报，但使用 `--scoring strict`（阈值 5/10），只推荐高价值技能。跳转到 §扫描执行。
4. **异常降级（网络/API 不可用）** → 用上次基线 + 标注"本周扫描失败，以下为上周数据"。详见 §降级。

---

## §扫描执行

### Step 1: 数据采集

**1a. skills.sh 首页 Leaderboard**

```bash
web_extract https://skills.sh/  → 提取 top 技能名、安装量、趋势
```

**1b. 8 类关键词扫描**

```bash
for query in "deployment" "testing" "security" "design" "code-review" "debugging" "workflow" "documentation"; do
  echo "=== $query ==="
  echo "" | npx skills find "$query" 2>&1
done
```

**1c. GitHub 搜索新技能**

搜索最近一周发布的 SKILL.md：
`site:github.com "SKILL.md" "agent skills" created:>$(date -d '7 days ago' +%Y-%m-%d)`

### Step 2: 汇总为 JSON

将采集结果整理为 `--input` 格式的 JSON 文件（`/tmp/radar_scan_YYYY-MM-DD.json`）：

```json
[
  {
    "name": "owner/repo@skill",
    "installs": "50000",
    "description": "一句话描述",
    "category": "deployment|testing|...",
    "has_scripts": true,
    "repo": "owner/repo"
  }
]
```

### Step 3: 调用数据处理黑盒

```bash
python scripts/skill_radar_scan.py \
  --input /tmp/radar_scan_YYYY-MM-DD.json \
  --baseline ~/.hermes/memory/skill-radar-baseline.md \
  --output /tmp/radar_report.md \
  --scoring normal     # 例行周报用 normal，临时扫描用 strict
```

详见 `scripts/skill_radar_scan.py --help`。脚本自动完成：去重、基线对比、消化评分、周报格式化、基线更新。

评分规则详见 `references/scoring-rules.md`。

---

## §输出与推送

### 推送到 Telegram

```bash
send_message --target telegram --message "$(cat /tmp/radar_report.md)"
```

### Cron 配置

- **频率**：每周一 09:00
- **Deliver**：telegram（直接推送到用户）
- **Prompt**：自包含，不含当前会话上下文

---

## §降级

| 失败环节 | 降级方案 |
|----------|----------|
| skills.sh 不可达 | 跳过 1a，只跑 1b + 1c |
| npx skills find 失败 | 降级为 web_search 替代 |
| GitHub 搜索超时 | 跳过 1c，标注"GitHub 搜索跳过" |
| 脚本处理失败 | 用原始列表生成简化报告 |
| 全部不可用 | 推送"本周雷达扫描失败" + 上周基线数据 |

---

## 验证与复盘

- **单次验证**：确认 Telegram 推送成功 + 基线文件已更新
- **定期复盘**：每月检查一次"值得关注→实际消化"的转化率
- **改进记录**：`references/scoring-rules.md` 中的评分权重可根据转化率调整

---

## 参考文件

| 文件 | 何时加载 |
|------|----------|
| `scripts/skill_radar_scan.py` | 不加载源码，直接 `--help` 后调用 |
| `references/skills-ecosystem-overview.md` | 需要了解生态概况或咱家已有技能矩阵时 |
| `references/scoring-rules.md` | 需要理解或调整消化评分逻辑时 |
| `~/.hermes/docs/hermes-skill-refactoring-spec-v1.md` | 需要了解本技能重构依据时 |
