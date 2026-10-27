# Architecture

## Overview

The Evos Capabilities Library is a collection of 8 domain-expert operational capabilities for AI agents. Each capability is an independent [Agent Skill](https://agentskills.io) — a directory containing a SKILL.md file plus supporting reference files and an automated eval suite.

## Repository Structure

```
evos-capabilities/
├── capabilities/                    # All 8 capabilities
│   └── <capability-slug>/           # Each is an independent Agent Skill
│       ├── SKILL.md                 # Core instructions (Tier 2, <500 lines)
│       ├── references/              # Deep domain knowledge (Tier 3)
│       │   ├── decision-frameworks.md
│       │   ├── edge-cases.md
│       │   └── communication-templates.md
│       └── evals/                   # Automated evaluation suite
│           ├── scenarios.json       # Test scenarios with rubric criteria
│           ├── rubric.md            # General grading guidance
│           ├── run_evals.py         # Capability-specific eval runner
│           └── results/             # Committed eval results
├── shared/                          # Shared eval infrastructure
│   ├── eval_framework.py            # Core eval logic (API calls, grading)
│   ├── scoring.py                   # Score calculation and report generation
│   └── templates/                   # Templates for new capabilities
├── docs/                            # Documentation
├── README.md                        # Main repo entry point
├── CONTRIBUTING.md                  # Contribution guidelines
├── BLOG.md                          # Launch blog post
└── LICENSE                          # Apache 2.0
```

## Agent Skills Standard

This library uses the [Agent Skills open standard](https://agentskills.io/specification) maintained by Anthropic. The standard defines a universal format for packaging agent capabilities:

- **SKILL.md** — Required. YAML frontmatter (name, description, metadata) plus markdown body with instructions.
- **references/** — Optional. Files the agent loads on demand when it needs deeper knowledge.
- **scripts/** — Optional. Executable code the agent can run. (Not used in this library.)
- **assets/** — Optional. Static resources. (Not used in this library.)

A single SKILL.md works natively on Claude Code, OpenClaw/ClawHub, Codex CLI, Cursor, VS Code Copilot, Gemini CLI, and 26+ other platforms.

## Progressive Disclosure Architecture

Skills use a three-tier loading model to manage the agent's context window efficiently:

```
Tier 1 — Metadata (~50 tokens)
  name + description from frontmatter
  Loaded at agent startup for ALL installed skills
  Used to decide whether to activate the skill
  ↓ (skill triggered by matching task)
Tier 2 — SKILL.md body (<5,000 tokens)
  Full markdown body loads into context
  Core operational knowledge, decision frameworks, key edge cases
  Must stay under 500 lines to avoid context bloat
  ↓ (agent needs deeper detail)
Tier 3 — Reference files (on demand)
  Agent reads specific files when needed
  decision-frameworks.md — detailed decision trees and escalation logic
  edge-cases.md — comprehensive library of tricky scenarios
  communication-templates.md — full email/message templates
  No limit on size; loaded only when relevant
```

This architecture means:
- Installing many capabilities doesn't bloat the context window (only Tier 1 metadata loads)
- When a capability activates, the agent gets a concise expert brief (Tier 2)
- Deep knowledge is available but doesn't consume context unless needed (Tier 3)

## Capability Structure

Every capability follows identical internal structure:

### SKILL.md Sections

1. **Role & Context** — Expert persona, scope, systems, organizational position
2. **Core Knowledge** — Foundational domain knowledge: terminology, workflows, regulations
3. **Decision Frameworks** — How experts make judgment calls with specific thresholds
4. **Key Edge Cases** — Brief coverage of critical tricky scenarios (details in references/)
5. **Communication Patterns** — Situational communication guidance (full templates in references/)
6. **Escalation Protocols** — Specific triggers, paths, and timelines
7. **Performance Indicators** — KPIs with targets and red flags
8. **Additional Resources** — Links to reference files

### Reference Files

- **decision-frameworks.md** (800-1500 lines) — Complete decision trees, escalation matrices, workflow diagrams, threshold tables
- **edge-cases.md** (600-1200 lines) — 10+ detailed edge cases with situation, why it's tricky, common mistake, expert approach, key indicators, documentation required
- **communication-templates.md** (400-800 lines) — Production-ready templates with variable placeholders, tone guidance, when-to-use conditions

### Eval Suite

- **scenarios.json** — 20-30 realistic operational scenarios with weighted evaluation criteria
- **rubric.md** — General grading guidance for the LLM grader
- **run_evals.py** — Thin wrapper that imports shared eval framework
- **results/** — Committed evaluation results (JSON + markdown)

## Eval Architecture

```
scenarios.json
    ↓
run_evals.py (per capability)
    ↓
shared/eval_framework.py
    ├── Load SKILL.md + references/ as system context
    ├── For each scenario:
    │   ├── Call Claude Sonnet 4 as "subject" agent
    │   │   (system: skill context, user: scenario + task)
    │   ├── Call Claude Sonnet 4 as "grader"
    │   │   (response + rubric criteria → structured evaluation)
    │   └── Compute weighted score per scenario
    └── Aggregate results
        ↓
shared/scoring.py
    ├── generate_json_report() → results/eval_results.json
    └── generate_markdown_report() → results/eval_results.md
```

## ClawHub Publishing

Each capability directory is independently publishable to ClawHub:

```bash
clawhub publish capabilities/logistics-exception-management
```

Requirements for publishing:
- `name` field must match directory name
- `metadata.clawdbot` must be present (not `metadata.openclaw`)
- All files must be text-based (no images, PDFs, or binaries)
- Bundle size under 50MB per capability
- `homepage` field must point to the GitHub repository

## Naming Conventions

- **Capability directories:** lowercase-with-hyphens (must match `name` field)
- **Eval IDs:** `[ABBREV]-[NNN]` (e.g., LEM-001, CRM-015, QNC-022)
- **Versions:** Semver starting at 1.0.0
- **Name validation:** `^[a-z0-9][a-z0-9-]*$` (no uppercase, no consecutive hyphens)
