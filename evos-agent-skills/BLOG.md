# Why We're Open-Sourcing Operational Expertise for AI Agents

AI agents are remarkably capable. They can write code, analyse documents, search the web, and reason through complex problems. But ask one to handle a freight exception involving a temperature-controlled pharmaceutical shipment with a disputed reefer failure, and you'll get a response that would make any logistics professional wince.

The gap isn't intelligence. It's experience.

## The Problem: Smart Agents, No Judgment

A seasoned freight exceptions analyst knows that when a carrier claims the reefer unit maintained correct temperature, you don't accept their set-point reading — you demand the continuous temperature recorder download and look at the return-air temperature trend. They know the difference between a scan gap and a lost shipment. They know that filing a standard damage claim for a temperature excursion on a pharmaceutical shipment is wrong — you need a formal temperature excursion notice to preserve your rights under both Carmack and any pharma-specific contract terms.

This kind of knowledge doesn't come from documentation or training materials. It comes from handling thousands of exceptions over 15 years and learning, often the hard way, what works and what doesn't.

Today's AI agents don't have access to this knowledge. They have general intelligence and broad training data, but not the specific operational judgment that separates a veteran from a new hire. The result is agents that give advice like "contact the carrier about the issue and file a claim" — technically correct and operationally useless.

## What We Built

The Evos Capabilities Library is a collection of 8 operational capabilities that codify real domain expertise into a format any AI agent can use. Each capability covers a specific operational domain — logistics, retail, manufacturing, or energy — and contains the knowledge that would take years of hands-on experience to develop.

We're releasing it under Apache 2.0 because we believe operational expertise should be accessible, verifiable, and improvable by the community.

### What's Inside Each Capability

Every capability follows a three-tier progressive disclosure architecture built on the Agent Skills open standard:

**Tier 1 — Metadata.** A name and description that tells agents when to activate the capability. This is all that loads at startup, keeping context windows lean.

**Tier 2 — Core Instructions.** Under 500 lines of the most important operational knowledge: terminology, decision frameworks, escalation triggers, key edge cases. Think of it as the senior brief — everything an experienced operator would tell a capable new hire on day one.

**Tier 3 — Deep Reference.** Detailed decision trees, comprehensive edge case libraries, and production-ready communication templates. The agent loads these on demand, only when it needs the depth.

The edge cases file is the most important piece. It covers the tricky situations where non-experts get it wrong — the pharma reefer dispute, the consignee dock damage masquerading as transit damage, the broker insolvency with cargo held hostage. Each edge case documents the situation, why it's tricky, what the common mistake is, and what the expert does instead. This is the knowledge that can only come from having been there.

### The 8 Capabilities

We started with domains where operational expertise creates the largest gap between novice and veteran performance:

- **Logistics Exception Management** — freight exceptions, carrier disputes, claims processes
- **Carrier Relationship Management** — rate negotiation, scorecarding, portfolio strategy
- **Customs & Trade Compliance** — tariff classification, duty optimisation, restricted party screening
- **Inventory Demand Planning** — forecasting, safety stock, promotional planning
- **Returns & Reverse Logistics** — disposition decisions, fraud detection, vendor recovery
- **Production Scheduling** — job sequencing, bottleneck resolution, disruption response
- **Quality & Non-Conformance** — NCR investigation, root cause analysis, CAPA management
- **Energy Procurement** — tariff optimisation, demand charge management, PPA evaluation

## Why Evals Matter

Every open-source agent skill library makes claims about quality. We wanted to back ours up with evidence.

Each capability ships with 20-30 automated evaluation scenarios — realistic operational situations graded against domain-specific rubrics. The eval pipeline works like this: Claude Sonnet 4 receives the capability as context and the scenario as a task, generates a response, and then a separate Claude instance grades the response against specific pass/fail criteria.

The scenarios aren't softballs. Roughly 30% are hard scenarios designed so that a generic agent without the capability fails meaningfully. If an agent without our logistics exception management capability can pass the pharma reefer temperature dispute scenario, that scenario isn't testing expertise — it's testing general reasoning. Our hard scenarios test the judgment calls that only come from deep domain exposure.

201 total scenarios across 8 capabilities, averaging 93.2% on domain-expert rubrics. Every one designed to feel like it was pulled from a real operations team's case files. The results are committed to the repo — run them yourself to verify.

But scores alone don't prove the capabilities add value. Claude Sonnet 4 is a strong general-purpose model — maybe it handles these scenarios fine without any domain context? We ran the exact same 201 scenarios on the bare model with zero system prompt — just the raw scenario as a user message, exactly like pasting it into the Claude application. No role instruction, no domain coaching. Same grader, same rubric, one variable changed.

The bare model averaged 81.4%. With capabilities loaded, 93.2% — an 11.8 percentage point lift. The gap is widest where domain specificity matters most: energy procurement jumped from 77.4% to 95.4% (+18.0pp), returns & reverse logistics from 70.3% to 88.0% (+17.7pp), and customs & trade compliance from 74.6% to 90.4% (+15.8pp). These are domains where the bare model doesn't just lack nuance — it gives actively wrong advice on regulatory filings, financial thresholds, and procedural sequences.

The baseline results are committed alongside the skill-equipped results. Run `--baseline` on any capability to reproduce.

## Built for Every Platform

The library uses the Agent Skills open standard (agentskills.io), which means each capability works natively on Claude Code, OpenClaw/ClawHub, Codex CLI, Cursor, VS Code Copilot, Gemini CLI, and 26+ other agent platforms. One format, universal compatibility. No platform-specific variants needed.

Install a single capability in under 60 seconds, or install all eight. Each is independently publishable and independently usable.

## What We're Asking For

We're releasing these capabilities because we believe the community can make them better. If you have 10+ years of operational experience in any of these domains and you see something we got wrong, or an edge case we missed, or a decision framework that doesn't match how it actually works in practice — we want to hear from you.

We're also interested in new domains. If you have deep expertise in an operational area not yet covered and want to codify it into a capability, the contributing guide has everything you need.

The goal is a library that domain experts look at and say "yes, that's exactly how it works." We're not there yet on every detail. Help us get closer.

## About Evos

Evos turns decades of operational expertise into autonomous AI systems that handle workloads 24/7 — designed to work the way top performers already do. This library is the open-source knowledge layer that underpins that mission. Learn more at [getevos.ai](https://getevos.ai).
