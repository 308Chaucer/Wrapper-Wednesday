# Adding New Capabilities

This guide walks through creating a new capability for the Evos Capabilities Library. A capability is an Agent Skill that codifies deep domain expertise into a format any AI agent can use.

## Prerequisites

- **Deep domain expertise.** You should have 10+ years of operational experience in the domain, or work closely with someone who does. Surface-level knowledge will not pass review.
- **Familiarity with the existing capabilities.** Read at least one complete capability (SKILL.md + all references + eval scenarios) to understand the quality bar and structural conventions.

## Step-by-Step Process

### 1. Propose the Capability

Open a GitHub issue titled "Capability Proposal: [Name]" with:

- **Domain:** What operational area does this cover?
- **Expert persona:** Who is the professional this codifies? (e.g., "Senior procurement manager at a Fortune 500 manufacturer")
- **Why it matters:** What does this expert know that a generic AI agent doesn't?
- **Sample edge cases:** 3-5 specific scenarios where only deep experience gets the right answer
- **Overlap check:** How does this differ from existing capabilities?

Wait for approval before building.

### 2. Choose a Slug

The capability slug becomes both the directory name and the `name` field in SKILL.md frontmatter. They must match exactly.

Rules:
- Lowercase letters, numbers, and hyphens only
- No consecutive hyphens (`--`)
- Cannot start or end with a hyphen
- 1-64 characters
- Must be URL-safe
- Pattern: `^[a-z0-9][a-z0-9-]*$`

Examples: `logistics-exception-management`, `energy-procurement`, `quality-nonconformance`

### 3. Create the Directory Structure

```bash
mkdir -p capabilities/<slug>/references capabilities/<slug>/evals/results
```

Or copy from the template:

```bash
cp -r shared/templates/capability-template capabilities/<slug>
```

### 4. Write SKILL.md

Start with the template at `shared/templates/SKILL_TEMPLATE.md`.

#### Frontmatter

```yaml
---
name: <slug>
description: >
  One-paragraph description. Include: what it does, the expert persona,
  and trigger phrases ("Use when..."). Be keyword-rich — this is how
  agent platforms decide whether to activate the skill.
license: Apache-2.0
version: 1.0.0
homepage: https://github.com/evos-ai/evos-capabilities
metadata:
  author: evos
  clawdbot:
    emoji: "<relevant emoji>"
---
```

Critical:
- `name` must match directory name exactly
- Use `metadata.clawdbot` not `metadata.openclaw`
- `description` must include trigger phrases and be keyword-rich

#### Body Sections

Follow the standard 8-section structure used by all capabilities:

1. **Role & Context** (5-10 lines)
2. **Core Knowledge** (60-80 lines)
3. **Decision Frameworks** (40-60 lines)
4. **Key Edge Cases** (30-40 lines)
5. **Communication Patterns** (20-30 lines)
6. **Escalation Protocols** (15-20 lines)
7. **Performance Indicators** (10-15 lines)
8. **Additional Resources** (5-10 lines)

Total body must be under 500 lines. Move deep content to reference files.

### 5. Write Reference Files

#### references/decision-frameworks.md (800-1500 lines)

Comprehensive decision trees, escalation matrices, threshold tables, and workflow logic. This is where detailed conditional logic lives that would bloat SKILL.md.

#### references/edge-cases.md (600-1200 lines)

At least 10 detailed edge cases. Each must include:
- **Situation:** Textured, realistic scenario with specifics
- **Why It's Tricky:** What makes it non-obvious
- **Common Mistake:** What a less experienced person does wrong
- **Expert Approach:** Step-by-step resolution
- **Key Indicators:** Signals an expert looks for
- **Documentation Required:** Specific paperwork needed
- **Resolution Timeline:** Realistic timeline

This is the most important reference file. It's what makes a capability feel like it was written by someone who has actually done the job.

#### references/communication-templates.md (400-800 lines)

Full templates with `{{variable}}` placeholders. Each template needs:
- Subject line
- Full body text
- Tone guidance
- When to use
- What NOT to say

### 6. Build the Eval Suite

#### evals/scenarios.json

Follow the schema in `shared/templates/scenarios_template.json`. Requirements:

- 20+ scenarios minimum
- Difficulty mix: ~30% easy, ~40% medium, ~30% hard
- 3-5 evaluation criteria per scenario, weights summing to 1.0
- Specific pass/fail rubric descriptions
- Realistic context with dollar amounts, company names, timelines
- ID format: `[ABBREV]-[NNN]` (e.g., `MYC-001`)

#### evals/rubric.md

General grading guidance for the LLM grader. Define what "domain expertise" vs "generic response" means for this specific domain.

#### evals/run_evals.py

Use this standard wrapper:

```python
#!/usr/bin/env python3
"""Eval runner for <Capability Name> capability."""
import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "shared"))
from eval_framework import main
if __name__ == "__main__":
    if "--capability" not in sys.argv:
        capability_dir = Path(__file__).resolve().parent.parent
        sys.argv.extend(["--capability", str(capability_dir)])
    main()
```

### 7. Validate

Before submitting a PR, check:

- [ ] SKILL.md body is under 500 lines (`wc -l capabilities/<slug>/SKILL.md`)
- [ ] `name` field matches directory name
- [ ] Frontmatter uses `metadata.clawdbot`
- [ ] All required frontmatter fields present (name, description, license, version, homepage, metadata)
- [ ] scenarios.json is valid JSON (`python3 -c "import json; json.load(open('scenarios.json'))"`)
- [ ] All criteria weights sum to 1.0 per scenario
- [ ] Difficulty mix is approximately 30/40/30
- [ ] No placeholder text (search for TODO, TBD, INSERT, PLACEHOLDER)
- [ ] All reference file links in SKILL.md are valid
- [ ] No binary files in the capability directory
- [ ] run_evals.py imports without errors

### 8. Submit PR

Open a pull request with:
- Clear description of the domain and your expertise
- Summary of what the capability covers
- Eval scenario count and difficulty distribution
- Any domain-specific considerations for reviewers
