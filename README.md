# Rehearsal Coach

An adversarial rehearsal engine for public speaking, interviews, webinars, and high-stakes meetings.

## What this repo includes

- A deterministic **Chaos Mode** engine that injects pressure events from live performance metrics.
- A persona-aware interruption script library (VC, CEO, board, academic, moderator).
- A scoring model for resilience (recovery speed, message integrity, language control, presence, decision clarity).
- Unit tests for event triggering, cooldown behavior, and scoring.

## Quick start

```bash
python -m unittest discover -s tests -v
```

## Core concepts

- **PerformanceSnapshot**: current speaking telemetry (pace, filler count, eye contact, jargon, etc.).
- **ChaosEvent**: injected stressor with script, severity, recovery window, and score weight.
- **ChaosEngine**: rules + cooldown + max-events policy.
- **ResilienceScorer**: computes 0-100 resilience score from recovery dimensions.

