# Evos Capabilities

**Open-source operational capabilities for AI agents — codified from domain experts with decades of real-world experience. Works with Claude Code, OpenClaw, Codex CLI, Cursor, and any Agent Skills-compatible platform.**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Capabilities](https://img.shields.io/badge/Capabilities-8-green.svg)](#capabilities)
[![Agent Skills](https://img.shields.io/badge/Agent_Skills-Compatible-purple.svg)](https://agentskills.io)
[![Eval Verified](https://img.shields.io/badge/Eval_Verified-201_scenarios-orange.svg)](#capabilities)
[![Avg Score](https://img.shields.io/badge/Avg_Score-93.2%25-brightgreen.svg)](#capabilities)
[![Lift vs Baseline](https://img.shields.io/badge/Avg_Lift-+11.8pp_vs_bare_model-yellow.svg)](#baseline-comparison)

## What This Is

Evos translates and codifies decades of learned expertise, from professionals working in traditional industries. This library is the knowledge layer that makes evos agentic systems perform like experienced operators — not by prompt engineering, but by codifying the judgment calls, edge cases, escalation logic, and domain-specific knowledge that separates a 20-year veteran from a new hire. Each capability contains expertise from real professionals with 10-20+ years of operational experience. We're open-sourcing it so any AI agent on any platform can access it.

## Capabilities

| Capability | Industry | Scenarios | Eval Score | Description |
|---|---|---|---|---|
| [Logistics Exception Management](capabilities/logistics-exception-management/) | Logistics | 30 | **95.0%** | Freight exceptions, shipment delays, damages, losses, carrier disputes |
| [Carrier Relationship Management](capabilities/carrier-relationship-management/) | Logistics | 22 | **99.3%** | Rate negotiation, carrier scorecarding, portfolio strategy, RFP process |
| [Customs & Trade Compliance](capabilities/customs-trade-compliance/) | Logistics | 28 | **90.4%** | Tariff classification, duty optimisation, restricted party screening |
| [Inventory Demand Planning](capabilities/inventory-demand-planning/) | Retail | 24 | **93.0%** | Demand forecasting, safety stock, replenishment, promotional planning |
| [Returns & Reverse Logistics](capabilities/returns-reverse-logistics/) | Retail | 24 | **88.0%** | Returns authorisation, disposition, fraud detection, vendor recovery |
| [Production Scheduling](capabilities/production-scheduling/) | Manufacturing | 23 | **92.4%** | Job sequencing, changeover optimisation, bottleneck resolution |
| [Quality & Non-Conformance](capabilities/quality-nonconformance/) | Manufacturing | 26 | **91.9%** | NCR investigation, root cause analysis, CAPA, SPC, supplier quality |
| [Energy Procurement](capabilities/energy-procurement/) | Energy | 24 | **95.4%** | Tariff optimisation, demand charge management, PPA evaluation |

## Baseline Comparison

Does the capability context actually make a difference? We ran every scenario twice on the same model (Claude Sonnet 4) — once with the full capability loaded, once with no domain context at all. The baseline receives zero system prompt — just the raw scenario as a user message, exactly like pasting it into the Claude application. Same scenarios, same rubric, same grader. The only variable is whether the agent has the SKILL.md and reference files.

| Capability | Bare Model | With Capability | Lift |
|---|---|---|---|
| Logistics Exception Management | 85.2% | **95.0%** | +9.8pp |
| Carrier Relationship Management | 90.3% | **99.3%** | +9.0pp |
| Customs & Trade Compliance | 74.6% | **90.4%** | +15.8pp |
| Inventory Demand Planning | 84.7% | **93.0%** | +8.3pp |
| Returns & Reverse Logistics | 70.3% | **88.0%** | +17.7pp |
| Production Scheduling | 85.0% | **92.4%** | +7.4pp |
| Quality & Non-Conformance | 83.7% | **91.9%** | +8.2pp |
| Energy Procurement | 77.4% | **95.4%** | +18.0pp |
| **Average** | **81.4%** | **93.2%** | **+11.8pp** |

The lift is largest where the domain requires specific regulatory knowledge, financial thresholds, and procedural sequences that a general model hasn't memorised. Energy procurement (+18.0pp), returns & reverse logistics (+17.7pp), and customs & trade compliance (+15.8pp) show the biggest gains — these are domains where the wrong answer isn't just vague, it's actively harmful.

Run the baselines yourself: `python3 capabilities/<slug>/evals/run_evals.py --baseline --api-key $ANTHROPIC_API_KEY`

## Quick Start

Each capability is a standalone [Agent Skills](https://agentskills.io) directory. Install on any compatible platform:

### Claude Code

```bash
git clone https://github.com/evos-ai/evos-capabilities.git
cp -r evos-capabilities/capabilities/logistics-exception-management ~/.claude/skills/
```

### ClawHub / OpenClaw

```bash
clawhub install logistics-exception-management
```

### Cursor

```bash
git clone https://github.com/evos-ai/evos-capabilities.git
cp -r evos-capabilities/capabilities/logistics-exception-management .cursor/skills/
```

Replace `logistics-exception-management` with any capability slug from the table above.

## Why These Are Different

- **Expert-informed, not prompt-engineered.** Every capability is built from the operational knowledge of professionals with 10-20+ years in their domain. The edge cases, thresholds, and judgment frameworks come from real experience — not from paraphrasing textbooks.

- **Eval-verified with automated test suites.** Each capability ships with 20-30 realistic operational scenarios graded against domain-specific rubrics. No other open-source agent skill library provides verifiable evaluation.

- **Domain-specific edge cases and judgment calls.** The `references/edge-cases.md` file in each capability covers the tricky situations that trip up non-experts — the scenarios where the obvious approach is wrong and only experience tells you what to do instead.

- **Works everywhere — one format, 26+ platforms.** Built on the [Agent Skills open standard](https://agentskills.io). A single SKILL.md works on Claude Code, OpenClaw/ClawHub, Codex CLI, Cursor, VS Code Copilot, Gemini CLI, and 26+ other platforms.

## Before / After

**Scenario:** A temperature-controlled pharmaceutical shipment arrives with the carrier claiming the reefer unit maintained correct temperature throughout transit, but your facility's receiving inspection shows product temperature is 12°C above the required 2-8°C range.

**Generic agent response:**
> "Contact the carrier about the temperature issue. File a damage claim. Notify the customer about the delay. Consider finding a replacement shipment."

**Agent with Logistics Exception Management capability:**
> "This is a Level 4 severity (regulated product + temperature excursion). Immediate actions: (1) Quarantine the shipment — do not reject yet, you need it for evidence. (2) Download the continuous temperature recorder data (Sensitech/Emerson) from the shipment — this is your primary evidence, not the reefer unit's set-point reading. The carrier will point to their set-point; you need the return-air temperature trend showing when the excursion began. (3) Request the carrier's pre-trip inspection report and the reefer unit's download — if they resist, that's a red flag. (4) Notify your quality/regulatory team within 30 minutes per your pharma SOP. (5) File a formal temperature excursion notice with the carrier within 2 hours, not a standard damage claim — this preserves your rights under both Carmack and any pharma-specific contract terms. (6) Do NOT accept the carrier's claim that 'product was loaded warm' without comparing your dock temperature logs and the first 30 minutes of transit recorder data. If the recorder shows correct temp at origin and a mid-transit spike, the carrier's defense collapses."

## Running Evaluations

Each capability includes an automated eval suite that tests agent performance against domain-specific rubrics. Evals use Claude Sonnet 4 as both the subject agent and grader — 201 scenarios across all 8 capabilities, averaging **93.2%** with capabilities loaded vs **81.4%** bare model.

```bash
# Install dependency
pip install anthropic

# Run with capability context
python3 capabilities/logistics-exception-management/evals/run_evals.py \
  --api-key $ANTHROPIC_API_KEY

# Run baseline (no capability context) for comparison
python3 capabilities/logistics-exception-management/evals/run_evals.py \
  --baseline --api-key $ANTHROPIC_API_KEY

# Run a single scenario
python3 capabilities/logistics-exception-management/evals/run_evals.py \
  --scenario LEM-001 --api-key $ANTHROPIC_API_KEY
```

Results are saved as JSON and markdown in each capability's `evals/results/` directory. Both skill-equipped and baseline results from our latest runs are committed.

## Repository Structure

```
evos-capabilities/
├── capabilities/
│   └── <capability-slug>/     # Each is an independent Agent Skill
│       ├── SKILL.md            # Core instructions (<500 lines)
│       ├── references/         # Deep domain knowledge (loaded on demand)
│       └── evals/              # Automated evaluation suite
├── shared/                     # Shared eval framework
├── docs/                       # Architecture and methodology docs
├── CONTRIBUTING.md             # How domain experts contribute
└── BLOG.md                     # Why we built this
```

## Contributing

We welcome contributions from domain experts — you don't need to be a developer. If you have 10+ years of operational experience and see ways to improve a capability or add a new one, see [CONTRIBUTING.md](CONTRIBUTING.md).

## About Evos

Evos turns decades of operational expertise into autonomous AI systems that handle your workload 24/7. Learn more at [getevos.ai](https://getevos.ai).
