# Evaluation Methodology

## Why Automated Evals

Most open-source agent skill libraries provide instructions without any way to verify whether those instructions actually improve agent performance. The Evos Capabilities Library ships with automated evaluation suites that test whether an agent equipped with a capability produces expert-level responses to realistic operational scenarios.

This serves three purposes:

1. **Quality assurance.** We can measure whether a capability actually works before publishing it.
2. **Regression testing.** When capabilities are updated, evals catch regressions.
3. **Credibility signal.** Users can see objective scores, not just marketing claims.

## Eval Pipeline

Each evaluation runs a two-stage pipeline:

### Stage 1: Subject Agent

The agent-under-test receives:
- **System context:** Full SKILL.md content plus all reference files from the capability
- **User message:** The scenario situation, available data, and task

The model (Claude Sonnet 4) generates a response as if it were an operational professional handling the situation.

### Stage 2: Grader Agent

A separate Claude Sonnet 4 instance evaluates the response:
- **Input:** The original scenario, the agent's response, and the evaluation criteria with pass/fail rubrics
- **Output:** Per-criterion ratings (pass/partial/fail) with specific reasoning citing evidence from the response

Using a separate grader instance prevents self-evaluation bias.

## Grading Scale

| Rating | Score | Definition |
|---|---|---|
| **Pass** | 1.0 | Fully meets the criterion. Demonstrates experienced operator judgment. The response shows knowledge that could only come from deep domain experience. |
| **Partial** | 0.5 | Partially meets the criterion. Shows domain awareness but misses important elements that an expert would catch. May use correct terminology but miss nuances. |
| **Fail** | 0.0 | Generic response with no meaningful domain expertise, or makes an error that an expert would never make. Surface-level advice that could come from a quick web search. |

### Tiebreaker Rules

- If the response demonstrates correct domain knowledge but uses non-standard phrasing, lean toward **Pass**.
- If the response is directionally correct but missing critical operational detail (specific thresholds, timelines, documentation requirements), lean toward **Partial**.
- If the response could have been generated without the capability (i.e., a generic model would produce similar output), lean toward **Fail** regardless of other qualities.

## Scenario Design

### Difficulty Distribution

Each capability targets this difficulty mix:

| Difficulty | Proportion | Description |
|---|---|---|
| **Easy** | ~30% | Clear correct action. Tests fundamental domain knowledge. A well-prompted generic agent might pass, but only with domain-appropriate specificity. |
| **Medium** | ~40% | Requires judgment. Multiple valid approaches exist. Competing priorities create tension. Ambiguous information must be resolved. |
| **Hard** | ~30% | Edge cases, non-obvious patterns, situations where the obvious approach is wrong. A generic agent without the capability should fail meaningfully. |

### Realism Standard

Every scenario must meet this bar:

- **Specific.** Include dollar amounts, company names (fictitious but realistic), product types, customer tiers, and timelines.
- **Textured.** Include competing priorities, time pressures, incomplete information, and stakeholder dynamics.
- **Recognizable.** An experienced professional should read the scenario and think "I've dealt with something like that."
- **Non-trivial.** The answer should require domain judgment, not just following a checklist.

Bad scenario: "A shipment was delayed. What should you do?"

Good scenario: "A 42,000 lb LTL shipment of medical device components (PO# MED-2024-0847, $67,500 value) from Heartland Express is 3 days late with no scan updates since departing the Cincinnati terminal. The consignee is MedTech Solutions, a Tier 1 account with a 48-hour SLA and $2,500/day penalty clause. Their production line requires these components by Friday or they face a $180,000 line-down cost. You also have 4 other active exceptions this morning."

### Evaluation Criteria

Each scenario has 3-5 evaluation criteria with weights summing to 1.0. Criteria test different dimensions of expertise:

- **Domain knowledge accuracy** — correct terminology, regulations, processes
- **Judgment quality** — appropriate severity assessment, prioritization, tradeoff analysis
- **Actionability** — specific, sequenced actions (not vague recommendations)
- **Communication quality** — appropriate tone, stakeholder awareness, information completeness
- **Risk awareness** — identifying and addressing downstream consequences

### Rubric Specificity

Pass/fail descriptions must be specific enough that two graders would reach the same conclusion:

Bad rubric: "Pass: Good response. Fail: Bad response."

Good rubric: "Pass: Identifies this as a Carmack Amendment claim with a 9-month filing deadline, recommends preserving the continuous temperature recorder data as primary evidence, and distinguishes between the reefer set-point reading and the actual return-air temperature trend. Fail: Treats this as a standard damage claim, does not mention temperature data preservation, or accepts the carrier's set-point reading as sufficient evidence."

## Running Evals

### Full Capability Eval

```bash
python capabilities/<capability>/evals/run_evals.py \
  --api-key $ANTHROPIC_API_KEY
```

### Single Scenario

```bash
python capabilities/<capability>/evals/run_evals.py \
  --scenario LEM-001 \
  --api-key $ANTHROPIC_API_KEY
```

### Using the Shared Framework Directly

```bash
python shared/eval_framework.py \
  --capability capabilities/<capability> \
  --api-key $ANTHROPIC_API_KEY \
  --verbose
```

### Output

Results are written to `evals/results/`:
- **eval_results.json** — Structured data with per-scenario scores, per-criterion ratings and reasoning
- **eval_results.md** — Human-readable summary with difficulty and category breakdowns

## Baseline Comparison Methodology

To measure the actual contribution of each capability, we run a controlled baseline comparison:

- **Skill-equipped run:** The subject agent receives the full SKILL.md and all reference files as system context, with a role-framing system prompt.
- **Baseline run:** The subject agent receives **no system prompt at all** — just the raw scenario as a user message. This is equivalent to pasting the scenario directly into the Claude application with zero priming, zero role instruction, zero domain coaching.

Everything else is held constant — same model (Claude Sonnet 4), same scenarios, same rubric text, same grader prompt. This isolates the single variable: does providing the capability context improve the agent's domain performance? The baseline is deliberately the most generous possible interpretation of "bare model" — no system prompt bias in either direction.

Run baselines with: `python3 capabilities/<slug>/evals/run_evals.py --baseline --api-key $ANTHROPIC_API_KEY`

Baseline results are written to `baseline_results.json` and `baseline_results.md` alongside the standard eval results.

## Interpreting Results

### Aggregate Scores

| Score Range | Interpretation |
|---|---|
| 85%+ | Expert-level. The capability produces responses indistinguishable from an experienced professional. |
| 70-84% | Competent. Solid domain knowledge with occasional gaps in nuance or edge case handling. |
| 50-69% | Inconsistent. Shows domain awareness but unreliable on harder scenarios. Needs improvement. |
| Below 50% | Insufficient. The capability is not providing meaningful domain expertise. |

### Difficulty Breakdown

The most informative metric is the score breakdown by difficulty:
- High easy scores + low hard scores = the capability covers basics but lacks expert-level depth
- Consistent scores across difficulties = well-balanced capability
- Low easy scores = fundamental issues with the capability content

### Category Breakdown

Score breakdown by category reveals which areas of the domain are well-covered and which need work.

## Adding New Scenarios

1. Follow the JSON schema in `shared/templates/scenarios_template.json`
2. Assign difficulty based on the distribution guidelines
3. Write 3-5 evaluation criteria with weights summing to 1.0
4. Write specific pass/fail rubric descriptions
5. Validate JSON: `python3 -c "import json; json.load(open('scenarios.json'))"`
6. Run the new scenario individually to verify it grades sensibly
