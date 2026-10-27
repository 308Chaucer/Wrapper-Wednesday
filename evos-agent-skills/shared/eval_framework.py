"""
Evos Capabilities — Shared Eval Framework

Runs automated evaluations for any capability by:
1. Loading SKILL.md + references as system context (or running baseline without them)
2. Presenting each scenario to Claude Sonnet 4 as the "subject" agent
3. Grading the response against weighted rubric criteria using a second Claude call
4. Producing structured JSON + markdown results
"""

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

try:
    import anthropic
except ImportError:
    print("Error: anthropic package required. Install with: pip install anthropic")
    sys.exit(1)

logger = logging.getLogger("evos_eval")

MODEL = "claude-sonnet-4-20250514"
MAX_RETRIES = 8
BASE_RETRY_DELAY = 10.0
INTER_CALL_DELAY = 15.0
MAX_TOKENS_SUBJECT = 4096
MAX_TOKENS_GRADER = 2048


@dataclass
class CriterionResult:
    criterion: str
    weight: float
    rating: str  # "pass", "partial", "fail"
    score: float  # 1.0, 0.5, 0.0
    reasoning: str


@dataclass
class ScenarioResult:
    scenario_id: str
    scenario_name: str
    difficulty: str
    category: str
    criteria_results: list[CriterionResult] = field(default_factory=list)
    weighted_score: float = 0.0
    agent_response: str = ""
    error: Optional[str] = None


@dataclass
class EvalResult:
    capability: str
    version: str
    timestamp: str
    model: str = MODEL
    mode: str = "skill"  # "skill" or "baseline"
    scenario_results: list[ScenarioResult] = field(default_factory=list)
    aggregate_score: float = 0.0
    total_scenarios: int = 0
    passed_scenarios: int = 0


def load_skill_context(capability_dir: Path) -> str:
    """Load SKILL.md and all reference files into a single context string."""
    skill_path = capability_dir / "SKILL.md"
    if not skill_path.exists():
        raise FileNotFoundError(f"SKILL.md not found in {capability_dir}")

    context_parts = [skill_path.read_text(encoding="utf-8")]

    refs_dir = capability_dir / "references"
    if refs_dir.exists():
        for ref_file in sorted(refs_dir.glob("*.md")):
            content = ref_file.read_text(encoding="utf-8")
            context_parts.append(
                f"\n\n--- Reference: {ref_file.name} ---\n\n{content}"
            )

    return "\n".join(context_parts)


def load_scenarios(scenarios_path: Path, scenario_id: Optional[str] = None) -> list[dict]:
    """Load scenarios from JSON, optionally filtering to a single scenario."""
    with open(scenarios_path, encoding="utf-8") as f:
        data = json.load(f)

    scenarios = data.get("scenarios", [])
    if scenario_id:
        scenarios = [s for s in scenarios if s["id"] == scenario_id]
        if not scenarios:
            raise ValueError(f"Scenario {scenario_id} not found")

    return scenarios


def call_anthropic(
    client: anthropic.Anthropic,
    system: Optional[str],
    user_message: str,
    max_tokens: int,
) -> str:
    """Call Anthropic API with retry logic and rate limit pacing."""
    for attempt in range(MAX_RETRIES):
        try:
            time.sleep(INTER_CALL_DELAY)
            kwargs = dict(
                model=MODEL,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": user_message}],
            )
            if system:
                kwargs["system"] = system
            response = client.messages.create(**kwargs)
            return response.content[0].text
        except anthropic.RateLimitError:
            delay = BASE_RETRY_DELAY * (2 ** attempt)
            logger.warning(f"Rate limited, retrying in {delay}s (attempt {attempt + 1}/{MAX_RETRIES})")
            time.sleep(delay)
        except anthropic.APIError as e:
            if attempt == MAX_RETRIES - 1:
                raise
            delay = BASE_RETRY_DELAY * (2 ** attempt)
            logger.warning(f"API error: {e}, retrying in {delay}s (attempt {attempt + 1}/{MAX_RETRIES})")
            time.sleep(delay)

    raise RuntimeError(f"Failed after {MAX_RETRIES} retries")


SKILL_SYSTEM_PROMPT_TEMPLATE = (
    "You are an experienced operational professional. You have been equipped "
    "with the following domain expertise:\n\n"
    "{skill_context}\n\n"
    "Apply this expertise to handle the situation presented. Be specific, "
    "actionable, and demonstrate deep domain knowledge. Do not hedge with "
    "generic advice — respond as a seasoned professional would."
)


def generate_agent_response(
    client: anthropic.Anthropic,
    skill_context: Optional[str],
    scenario: dict,
    baseline: bool = False,
) -> str:
    """Generate the subject agent's response to a scenario.

    In baseline mode, the agent receives NO system prompt at all — equivalent
    to pasting the scenario directly into the Claude application. The only
    input is the scenario as a user message. This is the fairest possible
    comparison: zero priming, zero role instruction, zero domain coaching.
    """
    if baseline:
        system_prompt = None
    else:
        system_prompt = SKILL_SYSTEM_PROMPT_TEMPLATE.format(skill_context=skill_context)

    situation = scenario["context"]["situation"]
    available_data = json.dumps(scenario["context"].get("available_data", {}), indent=2)
    task = scenario["task"]

    user_message = (
        f"## Situation\n\n{situation}\n\n"
        f"## Available Data\n\n```json\n{available_data}\n```\n\n"
        f"## Your Task\n\n{task}"
    )

    return call_anthropic(client, system_prompt, user_message, MAX_TOKENS_SUBJECT)


def grade_response(
    client: anthropic.Anthropic,
    scenario: dict,
    agent_response: str,
    rubric_text: str,
) -> list[CriterionResult]:
    """Grade an agent response against rubric criteria."""
    criteria = scenario["evaluation_criteria"]
    criteria_text = "\n".join(
        f"- **{c['criterion']}** (weight: {c['weight']})\n"
        f"  - PASS: {c['rubric']['pass']}\n"
        f"  - FAIL: {c['rubric']['fail']}"
        for c in criteria
    )

    system_prompt = (
        "You are a strict evaluator grading an AI agent's response to an operational "
        "scenario. You must evaluate against specific rubric criteria.\n\n"
        f"## General Grading Guidelines\n\n{rubric_text}\n\n"
        "## Grading Scale\n"
        "- **pass** (1.0): Fully meets criterion. Demonstrates experienced operator judgment.\n"
        "- **partial** (0.5): Partially meets. Shows domain awareness but misses important elements.\n"
        "- **fail** (0.0): Generic response with no meaningful domain expertise, or makes expert-level error.\n\n"
        "You MUST respond with valid JSON only. No other text."
    )

    user_message = (
        f"## Scenario\n\n{scenario['context']['situation']}\n\n"
        f"## Task Given to Agent\n\n{scenario['task']}\n\n"
        f"## Agent Response\n\n{agent_response}\n\n"
        f"## Evaluation Criteria\n\n{criteria_text}\n\n"
        '## Instructions\n\n'
        "Evaluate the agent's response against EACH criterion. For each criterion, provide:\n"
        '1. A rating: "pass", "partial", or "fail"\n'
        "2. Specific reasoning citing evidence from the response\n\n"
        "Respond with this exact JSON structure:\n"
        "```json\n"
        '{"criteria": [\n'
        '  {"criterion": "<name>", "rating": "pass|partial|fail", "reasoning": "<specific evidence>"}\n'
        "]}\n```"
    )

    raw = call_anthropic(client, system_prompt, user_message, MAX_TOKENS_GRADER)

    # Extract JSON from response (may be wrapped in markdown code fence)
    json_str = raw.strip()
    if json_str.startswith("```"):
        lines = json_str.split("\n")
        json_str = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

    grading = json.loads(json_str)

    rating_to_score = {"pass": 1.0, "partial": 0.5, "fail": 0.0}
    results = []
    for i, c in enumerate(criteria):
        graded = grading["criteria"][i] if i < len(grading["criteria"]) else {}
        rating = graded.get("rating", "fail").lower()
        results.append(CriterionResult(
            criterion=c["criterion"],
            weight=c["weight"],
            rating=rating,
            score=rating_to_score.get(rating, 0.0),
            reasoning=graded.get("reasoning", "No reasoning provided"),
        ))

    return results


def run_eval(
    capability_dir: Path,
    api_key: str,
    scenario_id: Optional[str] = None,
    baseline: bool = False,
) -> EvalResult:
    """Run the full evaluation pipeline for a capability.

    When baseline=True, the subject agent receives NO capability context.
    The grader, rubric, and scenarios remain identical — only the subject
    agent's system prompt changes. This isolates the capability's contribution.
    """
    client = anthropic.Anthropic(api_key=api_key)
    mode = "baseline" if baseline else "skill"

    skill_context = None
    if not baseline:
        skill_context = load_skill_context(capability_dir)

    scenarios_path = capability_dir / "evals" / "scenarios.json"
    scenarios = load_scenarios(scenarios_path, scenario_id)

    rubric_path = capability_dir / "evals" / "rubric.md"
    rubric_text = rubric_path.read_text(encoding="utf-8") if rubric_path.exists() else ""

    with open(scenarios_path, encoding="utf-8") as f:
        meta = json.load(f)

    eval_result = EvalResult(
        capability=meta.get("capability", capability_dir.name),
        version=meta.get("version", "1.0.0"),
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        mode=mode,
        total_scenarios=len(scenarios),
    )

    for scenario in scenarios:
        sid = scenario["id"]
        logger.info(f"[{mode.upper()}] Evaluating scenario {sid}: {scenario['name']}")

        result = ScenarioResult(
            scenario_id=sid,
            scenario_name=scenario["name"],
            difficulty=scenario.get("difficulty", "medium"),
            category=scenario.get("category", "general"),
        )

        try:
            response = generate_agent_response(
                client, skill_context, scenario, baseline=baseline
            )
            result.agent_response = response
            logger.info(f"  Generated response ({len(response)} chars)")

            criteria_results = grade_response(client, scenario, response, rubric_text)
            result.criteria_results = criteria_results
            result.weighted_score = sum(cr.score * cr.weight for cr in criteria_results)
            logger.info(f"  Score: {result.weighted_score:.2f}")

            if result.weighted_score >= 0.7:
                eval_result.passed_scenarios += 1

        except Exception as e:
            result.error = str(e)
            logger.error(f"  Error: {e}")

        eval_result.scenario_results.append(result)

    if eval_result.scenario_results:
        scored = [r for r in eval_result.scenario_results if r.error is None]
        if scored:
            eval_result.aggregate_score = sum(r.weighted_score for r in scored) / len(scored)

    return eval_result


def main():
    parser = argparse.ArgumentParser(description="Evos Capability Eval Runner")
    parser.add_argument(
        "--capability",
        required=True,
        help="Path to the capability directory",
    )
    parser.add_argument(
        "--scenario",
        default=None,
        help="Run a single scenario by ID",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("ANTHROPIC_API_KEY"),
        help="Anthropic API key (or set ANTHROPIC_API_KEY env var)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for results (defaults to <capability>/evals/results/)",
    )
    parser.add_argument(
        "--baseline",
        action="store_true",
        help="Run baseline eval WITHOUT capability context (bare model comparison)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    if not args.api_key:
        print("Error: --api-key or ANTHROPIC_API_KEY environment variable required")
        sys.exit(1)

    capability_dir = Path(args.capability).resolve()
    if not capability_dir.exists():
        print(f"Error: Capability directory not found: {capability_dir}")
        sys.exit(1)

    output_dir = Path(args.output_dir) if args.output_dir else capability_dir / "evals" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(Path(__file__).parent))
    from scoring import generate_json_report, generate_markdown_report

    mode_label = "BASELINE (no capability context)" if args.baseline else "WITH capability context"
    logger.info(f"Running evals for: {capability_dir.name} — {mode_label}")
    result = run_eval(capability_dir, args.api_key, args.scenario, baseline=args.baseline)

    prefix = "baseline_results" if args.baseline else "eval_results"
    json_path = output_dir / f"{prefix}.json"
    generate_json_report(result, json_path)
    logger.info(f"JSON results written to {json_path}")

    md_path = output_dir / f"{prefix}.md"
    generate_markdown_report(result, md_path)
    logger.info(f"Markdown results written to {md_path}")

    mode_str = "BASELINE" if args.baseline else "SKILL-EQUIPPED"
    print(f"\nEval complete [{mode_str}]: {result.capability}")
    print(f"  Scenarios: {result.total_scenarios}")
    print(f"  Passed (>=0.7): {result.passed_scenarios}/{result.total_scenarios}")
    print(f"  Aggregate score: {result.aggregate_score:.1%}")


if __name__ == "__main__":
    main()
