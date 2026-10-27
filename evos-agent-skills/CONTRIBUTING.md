# Contributing to Evos Capabilities

We welcome contributions from domain experts, engineers, and anyone who wants to make AI agents more operationally competent. You don't need to be a developer to contribute — operational expertise is the most valuable thing you can bring.

## How to Contribute

### 1. Improve Existing Capabilities

The highest-impact contributions are improvements to existing capabilities:

- **Add edge cases** to `references/edge-cases.md` — if you've encountered a tricky operational scenario not covered, write it up
- **Refine decision frameworks** in `references/decision-frameworks.md` — correct thresholds, add missing branches, improve specificity
- **Add eval scenarios** to `evals/scenarios.json` — especially hard scenarios that test genuine domain expertise
- **Fix domain errors** — if you spot incorrect terminology, wrong regulatory references, outdated thresholds, or mischaracterised industry practice, please flag or fix it

### 2. Add a New Capability

If you have deep domain expertise (10+ years) in an operational area not yet covered, you can propose a new capability.

Before starting, open an issue titled "Capability Proposal: [Name]" with:
- The operational domain and your experience in it
- What expert knowledge this would codify (not generic advice)
- 3-5 example edge cases that only an expert would handle correctly
- Target industry and estimated eval scenario count

See [docs/ADDING_CAPABILITIES.md](docs/ADDING_CAPABILITIES.md) for the full process.

### 3. Report Issues

If you find errors in domain knowledge, broken eval scenarios, structural issues, or documentation problems, please open an issue with:
- Which file(s) are affected
- What's wrong (be specific)
- What the correct information is (if you know)

## Quality Standards

Every contribution must meet the library's quality bar:

### Content Quality

- **Specificity over generality.** "Communicate clearly" is not expertise. "When a carrier fails to respond within 4 hours, escalate to their regional account manager with Subject 'ESCALATION:' and CC your VP" is expertise.
- **Correct domain terminology.** Use the terms practitioners actually use. If you're unsure about a term, that's a signal you may need more research.
- **Concrete thresholds, not vague guidance.** Decision frameworks must include specific numbers, conditions, and triggers — not "use judgment."
- **Real edge cases.** Every edge case should feel like it was pulled from a real operations team's case file. Include specific product types, dollar amounts, timelines, and competing pressures.

### Technical Quality

- SKILL.md body must be under 500 lines
- SKILL.md frontmatter must include all required fields: `name`, `description`, `license`, `version`, `homepage`, `metadata.clawdbot`
- Directory name must match the `name` field exactly
- All reference files must be text-based (.md, .json, .py, .yaml)
- Eval scenarios must have valid JSON with criteria weights summing to 1.0
- No placeholder text, no TODOs, no "[insert here]"

### Eval Scenario Guidelines

- **Difficulty mix:** ~30% easy, ~40% medium, ~30% hard
- **Realism:** Every scenario must include specific dollar amounts, fictitious company names, product types, customer tiers, and timelines
- **Hard scenarios must be genuinely hard.** If a generic AI agent without the capability would pass, the scenario is too easy
- **Rubric specificity:** Pass/fail descriptions must describe specific observable behaviors, not vague qualities

## Submitting a Pull Request

1. Fork the repository and create a branch from `main`
2. Make your changes following the quality standards above
3. If you've added eval scenarios, validate the JSON: `python3 -c "import json; json.load(open('path/to/scenarios.json'))"`
4. If you've modified SKILL.md, verify it's under 500 lines: `wc -l capabilities/<name>/SKILL.md`
5. Open a PR with a clear description of what you changed and why
6. For domain knowledge changes, include your relevant experience so reviewers can assess the contribution

## Code of Conduct

Be respectful, constructive, and focused on making the capabilities better. We value domain expertise from all backgrounds and experience levels. Disagreements about operational practices are welcome — back them up with evidence or experience.

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.
