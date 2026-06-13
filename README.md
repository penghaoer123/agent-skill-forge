# Agent Skill Forge

> A methodology and toolkit for engineering AI agent skills that stay lean, trigger reliably, and don't rot.

## The Problem

Agent skills start simple. A few instructions in a markdown file. Then you add edge cases. Then workarounds for model quirks. Then changelogs, historical anchors, pitfall tables. Six months later you have a 900-line monster that eats context and confuses the agent more than it helps.

Most skill systems tell you *what* a skill file looks like. They don't tell you *how to keep it healthy* as it grows.

## What This Is

**Agent Skill Forge** is a battle-tested methodology for skill engineering — learned from refactoring a real multi-agent system with 175+ skills. It gives you:

1. **The Spec** — 9 design principles + 4 mandatory structural elements for every skill
2. **The Tool** — `skill-refactor`, a meta-skill that audits, splits, and creates skills that follow the spec from line one
3. **The Patterns** — decision-tree entries, progressive disclosure, handoff protocols, staleness tracking, and wrong-answer firewalls

## Quick Start

```bash
# Audit any skill against the spec
skill-refactor → "只评估" path → scoring report in 30 seconds

# Create a new skill that's spec-compliant from day one
skill-refactor → "新建" path → answer 4 questions → skeleton ready

# Refactor a bloated skill (500+ lines)
skill-refactor → "重构" path → audit → design split → execute → verify
```

## Core Principles

| # | Principle | What It Means |
|---|-----------|---------------|
| 1 | **Description is the Trigger** | Not a summary. A routing rule with keywords and anti-triggers. |
| 2 | **Progressive Disclosure** | 100 tokens always. Full body on demand. References only when needed. |
| 3 | **500-Line Cap** | If your SKILL.md exceeds 500 lines, you're doing it wrong. |
| 4 | **Scripts as Black Boxes** | Deterministic workflows live in `scripts/`. Agents call `--help`, not read source. |
| 5 | **Self-Contained Folder** | A skill is a directory. Everything it needs lives inside. |
| 6 | **Opinionated, Not Generic** | Teach the agent to make choices. Reject AI-sludge defaults. |
| 7 | **Iterate, Don't One-Shot** | Draft → eval → review → rewrite. Skills are grown, not written. |
| 8 | **Decision Tree First** | First screen tells the agent "which situation are you in?" |
| 9 | **Ground in Subject** | Real experience. Real failures. Real fixes. Not generic templates. |

## Repository Structure

```
agent-skill-forge/
├── README.md                           ← You are here
├── spec/
│   └── hermes-skill-spec-v1.md         ← Full specification (v1.1)
├── skills/
│   └── skill-refactor/                 ← The meta-skill itself
│       ├── SKILL.md
│       └── references/
│           └── scoring-checklist.md
└── examples/                           ← Reference implementations
```

## The Five Mandatory Elements

Every skill must have these, right after the YAML frontmatter:

```markdown
## 协议层 (Protocol Layer)
| Use when | <trigger conditions> |
| Do NOT use when | <anti-triggers> |
| Delegate to | <which assistant> |
| Reads knowledge | <knowledge graph nodes> |
| Done when | <completion condition> |

## §Handoff
- Trigger: <when to pass to another skill>
- Target: <target skill>
- Context: <what context to carry over>

## 入口决策 (Entry Decision Tree)
1. **Scenario A** → ...
2. **Scenario B** → ...
N. **Not sure** → <default behavior>

## §Core Flow
<Minimal execution body. Details in references.>

## 验证与复盘 (Verify & Review)
- Single-run verification: <how to confirm success>
- Periodic review: <when and what to re-examine>
```

## v1.1 Additions

- **Reference Metadata Headers** — Every `references/*.md` carries `staleness_risk`, `last_verified`, `owner_skill` so agents know what's trustworthy.
- **Bidirectional Handoff** — Skills don't just link out; they define "when to hand the user to another skill."
- **Wrong-Answer Firewall** — Each reference documents the most common model hallucinations for its domain. An anti-pattern section that directly constrains generation.

## Where This Comes From

This methodology was extracted from a real-world refactoring sprint:

- **hermes-agent**: 922 → 149 lines (-84%)
- **peanutbutter**: 608 → 148 lines (-76%)
- **skill-radar**: gained protocol layer + black-box script

The audit and design process was then encoded as `skill-refactor` — so the same methodology can be applied to any skill, in any agent system that uses the SKILL.md format.

## Compatibility

- **Format**: Follows the [Agent Skills](https://agentskills.io) standard (SKILL.md + YAML frontmatter)
- **Extensions**: Adds protocol layer, handoff, decision trees, and staleness tracking on top of the base spec
- **Agent-agnostic**: Designed for Hermes Agent but applicable to Claude Code, Codex, Cursor, and any agent that loads skills from markdown files

## License

MIT
