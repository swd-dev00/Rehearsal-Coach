# Rehearsal Coach

An adversarial rehearsal engine for public speaking, interviews, webinars, and high-stakes meetings.

## What this repo includes

- A deterministic **Chaos Mode** engine that injects pressure events from live performance metrics.
- Support for session guardrails: cooldowns, max events per session, and max concurrent active events.
- Active-event lifecycle controls (`resolve_event`) for real-time orchestration.
- A persona-aware interruption script library (VC, CEO, board, academic, moderator).
- A **synthetic audience simulator** that aggregates persona reactions into weighted sentiment, retention, and confusion metrics.
- A scoring model for resilience (recovery speed, message integrity, language control, presence, decision clarity).
- Unit tests for event triggering, cooldown behavior, concurrency rules, scoring, and simulated audience behavior.

## Quick start

```bash
python -m unittest discover -s tests -v
```

## Core concepts

- **PerformanceSnapshot**: current speaking telemetry (pace, filler count, eye contact, jargon, etc.) with validation.
- **ChaosEvent**: injected stressor with script, severity, recovery window, and score weight.
- **ChaosEngine**: rules + cooldown + active-event concurrency policy.
- **SimulationInput**: normalized rehearsal metrics used for virtual audience evaluation.
- **AudienceSimulator**: deterministic persona-based feedback engine for pre-live content testing.
- **ResilienceScorer**: computes 0-100 resilience score from recovery dimensions.

