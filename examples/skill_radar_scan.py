#!/usr/bin/env python3
"""skill_radar_scan.py — 外部技能雷达 · 数据处理黑盒

扫描结果 → 去重 · 基线对比 · 消化评分 → 格式化周报

Usage:
  python scripts/skill_radar_scan.py --help
  python scripts/skill_radar_scan.py --input scan_results.json --baseline baseline.md [--output report.md] [--scoring strict]
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


# ── 评分维度 ──────────────────────────────────────────────
# 每条"值得关注"的技能按以下维度打分（0-2分/维，满分10）
SCORING_DIMENSIONS = {
    "gap_match": "与咱家能力缺口的匹配度（0=已有覆盖, 2=填补明确空白）",
    "growth": "安装量增长趋势（0=停滞, 1=稳定增长, 2=暴涨>20%）",
    "scriptable": "是否可脚本化/黑盒化（0=纯知识, 1=有代码, 2=完整CLI）",
    "synergy": "是否可与现有技能合并互补（0=孤立, 2=强互补）",
    "uniqueness": "是否有咱家没有的独特能力（0=重复轮子, 2=独有）",
}


def parse_args():
    p = argparse.ArgumentParser(
        description="外部技能雷达 — 数据处理黑盒",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/skill_radar_scan.py --input /tmp/scan.json --baseline ~/.hermes/memory/skill-radar-baseline.md
  python scripts/skill_radar_scan.py --input /tmp/scan.json --baseline ~/.hermes/memory/skill-radar-baseline.md --output /tmp/report.md --scoring strict
        """,
    )
    p.add_argument("--input", required=True, help="扫描结果 JSON 文件路径")
    p.add_argument("--baseline", required=True, help="基线文件路径 (Markdown)")
    p.add_argument("--output", default=None, help="输出文件路径 (默认 stdout)")
    p.add_argument("--scoring", default="normal", choices=["normal", "strict"],
                   help="评分严格度 (normal: ≥3分推荐, strict: ≥5分推荐)")
    p.add_argument("--week", default=None, help="周标签，如 2026-W24 (默认自动计算)")
    return p.parse_args()


def load_scan_results(path: str) -> list[dict]:
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "results" in data:
        return data["results"]
    raise ValueError(f"Unexpected JSON structure in {path}")


def load_baseline(path: str) -> dict[str, dict]:
    """Parse baseline markdown table into {skill_name: {installs, repo, ...}}"""
    baseline = {}
    if not Path(path).exists():
        return baseline

    content = Path(path).read_text()
    in_table = False
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("| 技能"):
            in_table = True
            continue
        if in_table and line.startswith("|"):
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 3 and parts[0]:
                name = parts[0]
                try:
                    installs = int(parts[1].replace("K", "000").replace("M", "000000").replace(",", ""))
                except ValueError:
                    installs = 0
                repo = parts[2] if len(parts) > 2 else ""
                baseline[name] = {"installs": installs, "repo": repo}
    return baseline


def load_existing_skills() -> set[str]:
    """Discover existing Hermes skill names (from bundled_manifest + skill dirs)."""
    existing = set()

    # From bundled manifest
    manifest = Path.home() / ".hermes/skills/.bundled_manifest"
    if manifest.exists():
        for line in manifest.read_text().strip().split("\n"):
            if ":" in line:
                existing.add(line.split(":")[0])

    # From skill directories
    for skills_dir in [
        Path.home() / ".hermes/skills",
        Path.home() / ".hermes/profiles/gemini/skills",
    ]:
        if skills_dir.exists():
            for skill_dir in skills_dir.rglob("SKILL.md"):
                existing.add(skill_dir.parent.name)

    return existing


def deduplicate(skills: list[dict], existing: set[str]) -> tuple[list[dict], list[dict]]:
    """Split into new (uncovered) and covered."""
    new, covered = [], []
    for s in skills:
        name = s.get("name", "").lower().replace("@", "/")
        matched = False
        for e in existing:
            if e in name or name in e:
                matched = True
                break
        if matched:
            covered.append(s)
        else:
            new.append(s)
    return new, covered


def score_skill(skill: dict, baseline: dict, existing: set) -> tuple[int, dict]:
    """Score a single skill on 5 dimensions (0-2 each, max 10)."""
    scores = {}

    # 1. gap_match
    name_lower = skill.get("name", "").lower()
    if any(e in name_lower or name_lower in e for e in existing):
        scores["gap_match"] = 0
    else:
        scores["gap_match"] = 2

    # 2. growth
    prev = baseline.get(skill.get("name", ""), {})
    curr_installs = int(skill.get("installs", 0))
    prev_installs = prev.get("installs", 0)
    if prev_installs == 0:
        scores["growth"] = 1
    elif curr_installs > prev_installs * 1.2:
        scores["growth"] = 2
    elif curr_installs > prev_installs:
        scores["growth"] = 1
    else:
        scores["growth"] = 0

    # 3. scriptable
    has_scripts = skill.get("has_scripts", False)
    scores["scriptable"] = 2 if has_scripts else 0

    # 4. synergy
    category = skill.get("category", "")
    synergy_cats = {"deployment", "testing", "security", "workflow", "code-review"}
    scores["synergy"] = 2 if category in synergy_cats else 1

    # 5. uniqueness
    generic_cats = {"documentation", "template", "example"}
    scores["uniqueness"] = 0 if category in generic_cats else 1

    total = sum(scores.values())
    return total, scores


def build_report(
    new_skills: list[dict],
    covered: list[dict],
    baseline: dict,
    existing: set,
    week_label: str,
    scoring_threshold: int,
) -> str:
    """Generate formatted weekly report."""

    scored = []
    for s in new_skills:
        total, dims = score_skill(s, baseline, existing)
        scored.append((total, dims, s))
    scored.sort(key=lambda x: x[0], reverse=True)

    surges = []
    for s in new_skills:
        name = s.get("name", "")
        if name in baseline:
            prev = baseline[name]["installs"]
            curr = int(s.get("installs", 0))
            if prev > 0 and curr > prev * 1.2:
                surges.append((s, curr - prev))

    worthy = [(t, s) for t, d, s in scored if t >= scoring_threshold]

    lines = [
        f"📡 外部技能雷达 · {week_label}",
        "",
    ]

    lines.append(f"🆕 本周新增（{len(new_skills)}个）")
    for _, _, s in scored[:10]:
        lines.append(f"  • {s.get('name', '?')} ({s.get('installs', '?')} installs) — {s.get('description', '')[:80]}")
    if len(scored) > 10:
        lines.append(f"  ... 另有 {len(scored) - 10} 个")
    lines.append("")

    if surges:
        lines.append(f"📈 暴涨（{len(surges)}个 · 周增长>20%）")
        for s, delta in surges:
            lines.append(f"  • {s.get('name', '?')} → +{delta} 安装")
        lines.append("")

    if worthy:
        lines.append(f"🔍 值得关注的（{len(worthy)}个 · 评分≥{scoring_threshold}）")
        for total, s in worthy:
            name = s.get("name", "")
            category = s.get("category", "other")
            lines.append(f"  • {name} ({s.get('installs', '?')} installs) — 评分 {total}/10")
            lines.append(f"    类别：{category}")
            lines.append(f"    潜在价值：{s.get('description', '')[:120]}")
            lines.append(f"    skills.sh 链接：https://skills.sh/{name.replace('@', '/')}")
        lines.append("")

    if covered:
        lines.append(f"📉 我们已覆盖（{len(covered)}个 · 无需关注）")
        for s in covered[:5]:
            lines.append(f"  • {s.get('name', '?')} → 对应咱家 skill：{s.get('name', '')}")
        if len(covered) > 5:
            lines.append(f"  ... 另有 {len(covered) - 5} 个")
        lines.append("")

    lines.append("📊 本周统计")
    lines.append(f"  总扫描技能：{len(new_skills) + len(covered)} | 新增：{len(new_skills)} | 值得关注：{len(worthy)} | 已覆盖：{len(covered)}")
    lines.append(f"  评分阈值：≥{scoring_threshold}/10 ({'严格' if scoring_threshold >= 5 else '正常'})")
    lines.append("")

    return "\n".join(lines)


def update_baseline(new_skills: list[dict], baseline_path: str, week_label: str):
    """Update baseline with current scan results."""
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        f"## 基线 · {today} · {week_label}",
        "| 技能 | 安装量 | 仓库 |",
        "|------|--------|------|",
    ]
    for s in sorted(new_skills, key=lambda x: int(x.get("installs", 0)), reverse=True)[:50]:
        name = s.get("name", "")
        installs = s.get("installs", 0)
        repo = s.get("repo", name.split("@")[0] if "@" in name else "")
        lines.append(f"| {name} | {installs} | {repo} |")

    Path(baseline_path).parent.mkdir(parents=True, exist_ok=True)
    Path(baseline_path).write_text("\n".join(lines) + "\n")


def main():
    args = parse_args()
    skills = load_scan_results(args.input)
    baseline = load_baseline(args.baseline)
    existing = load_existing_skills()
    new_skills, covered = deduplicate(skills, existing)
    week_label = args.week or f"{datetime.now().year}-W{datetime.now().isocalendar()[1]:02d}"
    threshold = 5 if args.scoring == "strict" else 3
    report = build_report(new_skills, covered, baseline, existing, week_label, threshold)
    if args.output:
        Path(args.output).write_text(report)
        print(f"Report written to {args.output}")
    else:
        print(report)
    update_baseline(new_skills, args.baseline, week_label)
    if args.output:
        print(f"Baseline updated: {args.baseline}")


if __name__ == "__main__":
    main()
