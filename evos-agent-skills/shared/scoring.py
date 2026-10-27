"""
Evos Capabilities — Scoring Utilities

Provides scoring calculations and report generation for eval results.
"""

import json
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eval_framework import EvalResult


def score_scenario(criteria_results: list) -> float:
    """Compute weighted score from criterion results."""
    if not criteria_results:
        return 0.0
    return sum(cr.score * cr.weight for cr in criteria_results)


def aggregate_scores(scenario_results: list) -> dict:
    """Compute aggregate statistics from scenario results."""
    if not scenario_results:
        return {"overall": 0.0, "by_difficulty": {}, "by_category": {}, "total": 0, "passed": 0}

    scored = [r for r in scenario_results if r.error is None]
    if not scored:
        return {"overall": 0.0, "by_difficulty": {}, "by_category": {}, "total": len(scenario_results), "passed": 0}

    overall = sum(r.weighted_score for r in scored) / len(scored)

    by_difficulty = defaultdict(list)
    by_category = defaultdict(list)
    for r in scored:
        by_difficulty[r.difficulty].append(r.weighted_score)
        by_category[r.category].append(r.weighted_score)

    diff_scores = {k: sum(v) / len(v) for k, v in by_difficulty.items()}
    cat_scores = {k: sum(v) / len(v) for k, v in by_category.items()}
    passed = sum(1 for r in scored if r.weighted_score >= 0.7)

    return {
        "overall": overall,
        "by_difficulty": diff_scores,
        "by_category": cat_scores,
        "total": len(scenario_results),
        "passed": passed,
    }


def generate_json_report(eval_result: "EvalResult", output_path: Path) -> None:
    """Write structured JSON report to file."""
    data = asdict(eval_result)
    stats = aggregate_scores(eval_result.scenario_results)
    data["statistics"] = stats

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_markdown_report(eval_result: "EvalResult", output_path: Path) -> None:
    """Write human-readable markdown report to file."""
    stats = aggregate_scores(eval_result.scenario_results)
    mode = getattr(eval_result, "mode", "skill")
    mode_label = "Baseline (No Capability Context)" if mode == "baseline" else "With Capability Context"
    lines = [
        f"# Eval Results: {eval_result.capability}",
        "",
        f"**Mode:** {mode_label}  ",
        f"**Version:** {eval_result.version}  ",
        f"**Model:** {eval_result.model}  ",
        f"**Timestamp:** {eval_result.timestamp}  ",
        f"**Aggregate Score:** {stats['overall']:.1%}  ",
        f"**Passed (>=70%):** {stats['passed']}/{stats['total']}",
        "",
        "## Summary by Difficulty",
        "",
        "| Difficulty | Avg Score | Count |",
        "|---|---|---|",
    ]

    for diff in ["easy", "medium", "hard"]:
        if diff in stats["by_difficulty"]:
            count = sum(
                1 for r in eval_result.scenario_results
                if r.difficulty == diff and r.error is None
            )
            lines.append(f"| {diff.title()} | {stats['by_difficulty'][diff]:.1%} | {count} |")

    lines.extend([
        "",
        "## Summary by Category",
        "",
        "| Category | Avg Score | Count |",
        "|---|---|---|",
    ])

    for cat, score in sorted(stats["by_category"].items()):
        count = sum(
            1 for r in eval_result.scenario_results
            if r.category == cat and r.error is None
        )
        lines.append(f"| {cat} | {score:.1%} | {count} |")

    lines.extend([
        "",
        "## Scenario Details",
        "",
    ])

    for r in eval_result.scenario_results:
        status = "ERROR" if r.error else f"{r.weighted_score:.1%}"
        lines.append(f"### {r.scenario_id}: {r.scenario_name}")
        lines.append("")
        lines.append(f"**Difficulty:** {r.difficulty} | **Category:** {r.category} | **Score:** {status}")
        lines.append("")

        if r.error:
            lines.append(f"> Error: {r.error}")
        else:
            lines.append("| Criterion | Weight | Rating | Score |")
            lines.append("|---|---|---|---|")
            for cr in r.criteria_results:
                lines.append(f"| {cr.criterion} | {cr.weight} | {cr.rating} | {cr.score} |")

            lines.append("")
            for cr in r.criteria_results:
                lines.append(f"**{cr.criterion}:** {cr.reasoning}")
                lines.append("")

        lines.append("---")
        lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
