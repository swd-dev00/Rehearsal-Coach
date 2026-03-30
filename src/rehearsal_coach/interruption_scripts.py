"""Persona-specific interruption scripts for high-pressure rehearsal."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class PersonaScript:
    persona: str
    trigger_focus: str
    lines: List[str]


PERSONA_SCRIPTS: Dict[str, PersonaScript] = {
    "shark_tank_vc": PersonaScript(
        persona="Shark Tank VC",
        trigger_focus="No monetization language or business model detail",
        lines=[
            "Stop. Revenue model in one sentence. Now.",
            "I don't care about features yet. How do you make money this quarter?",
            "Give me CAC, LTV, and payback period in plain English.",
        ],
    ),
    "hard_line_academic": PersonaScript(
        persona="Hard-Line Academic Reviewer",
        trigger_focus="Claims without method, sample, or source support",
        lines=[
            "Define your method and sample size before continuing.",
            "Is that peer-reviewed evidence or internal opinion?",
            "State the limitation of your data in one sentence.",
        ],
    ),
    "busy_ceo": PersonaScript(
        persona="Busy CEO",
        trigger_focus="Long context, weak prioritization, slow progress to decision",
        lines=[
            "You have 45 seconds: decision, risk, and ask.",
            "I'm joining late. Summarize the case in 30 seconds.",
            "Skip history. What do you need from me today?",
        ],
    ),
    "skeptical_board_member": PersonaScript(
        persona="Skeptical Board Member",
        trigger_focus="Optimism without downside mitigation",
        lines=[
            "What breaks first, and what is your contingency?",
            "Why is this worth the risk right now?",
            "Show me one leading indicator that proves this is working.",
        ],
    ),
    "unprepared_moderator": PersonaScript(
        persona="Unprepared Moderator",
        trigger_focus="Transition instability and logistical disruption",
        lines=[
            "We're having slide issues. Continue off-book.",
            "We're over time. Wrap in 60 seconds.",
            "Q&A was cut. Deliver your strongest closing now.",
        ],
    ),
}
