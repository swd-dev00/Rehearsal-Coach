"""Synthetic audience simulation for rehearsal content pre-testing."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Iterable, List


@dataclass(frozen=True)
class AudiencePersona:
    """Audience segment with weighted sensitivity to communication factors."""

    name: str
    share_pct: float
    clarity_weight: float
    pacing_weight: float
    evidence_weight: float
    engagement_weight: float
    skepticism: float

    def __post_init__(self) -> None:
        _ensure_range("share_pct", self.share_pct, 0, 100)
        _ensure_range("clarity_weight", self.clarity_weight, 0, 1)
        _ensure_range("pacing_weight", self.pacing_weight, 0, 1)
        _ensure_range("evidence_weight", self.evidence_weight, 0, 1)
        _ensure_range("engagement_weight", self.engagement_weight, 0, 1)
        _ensure_range("skepticism", self.skepticism, 0, 1)


@dataclass(frozen=True)
class SimulationInput:
    """Normalized input metrics from a rehearsal pass."""

    clarity_score: float
    pacing_score: float
    evidence_score: float
    engagement_score: float

    def __post_init__(self) -> None:
        _ensure_range("clarity_score", self.clarity_score, 0, 1)
        _ensure_range("pacing_score", self.pacing_score, 0, 1)
        _ensure_range("evidence_score", self.evidence_score, 0, 1)
        _ensure_range("engagement_score", self.engagement_score, 0, 1)


@dataclass(frozen=True)
class PersonaReaction:
    persona: str
    sentiment_score: float
    confusion_risk: float
    retention_likelihood: float
    comment: str


@dataclass(frozen=True)
class AudienceReport:
    weighted_sentiment: float
    weighted_retention: float
    weighted_confusion: float
    top_risk: str
    reactions: List[PersonaReaction]


class AudienceSimulator:
    """Deterministic synthetic audience feedback from segmented personas."""

    def __init__(self, personas: Iterable[AudiencePersona], seed: int = 7) -> None:
        self.personas = list(personas)
        if not self.personas:
            raise ValueError("at least one persona is required")
        total_share = sum(p.share_pct for p in self.personas)
        if round(total_share, 4) != 100:
            raise ValueError("persona share_pct values must sum to 100")
        self._rng = Random(seed)

    def simulate(self, snapshot: SimulationInput) -> AudienceReport:
        reactions = [self._react(p, snapshot) for p in self.personas]

        weighted_sentiment = _weighted_avg(reactions, self.personas, "sentiment_score")
        weighted_retention = _weighted_avg(reactions, self.personas, "retention_likelihood")
        weighted_confusion = _weighted_avg(reactions, self.personas, "confusion_risk")

        top_risk = self._classify_top_risk(snapshot)
        return AudienceReport(
            weighted_sentiment=round(weighted_sentiment, 3),
            weighted_retention=round(weighted_retention, 3),
            weighted_confusion=round(weighted_confusion, 3),
            top_risk=top_risk,
            reactions=reactions,
        )

    def _react(self, persona: AudiencePersona, s: SimulationInput) -> PersonaReaction:
        sentiment = (
            persona.clarity_weight * s.clarity_score
            + persona.pacing_weight * s.pacing_score
            + persona.evidence_weight * s.evidence_score
            + persona.engagement_weight * s.engagement_score
            - (0.2 * persona.skepticism)
        )
        sentiment = _clamp(sentiment + self._rng.uniform(-0.03, 0.03), 0, 1)

        confusion = _clamp((1 - s.clarity_score) * (0.7 + 0.3 * persona.skepticism), 0, 1)
        retention = _clamp((0.6 * sentiment) + (0.4 * s.engagement_score), 0, 1)

        return PersonaReaction(
            persona=persona.name,
            sentiment_score=round(sentiment, 3),
            confusion_risk=round(confusion, 3),
            retention_likelihood=round(retention, 3),
            comment=self._build_comment(persona, sentiment, confusion),
        )

    @staticmethod
    def _classify_top_risk(s: SimulationInput) -> str:
        values = {
            "clarity": s.clarity_score,
            "pacing": s.pacing_score,
            "evidence": s.evidence_score,
            "engagement": s.engagement_score,
        }
        lowest = min(values, key=values.get)
        return f"{lowest}_deficit"

    @staticmethod
    def _build_comment(persona: AudiencePersona, sentiment: float, confusion: float) -> str:
        if confusion > 0.45:
            return f"{persona.name}: I'm losing the thread—simplify and restate the core point."
        if sentiment > 0.75:
            return f"{persona.name}: Strong and persuasive—keep this framing."
        if persona.skepticism > 0.7:
            return f"{persona.name}: Good start, but I still need proof and quantified outcomes."
        return f"{persona.name}: Decent flow, but tighten transitions and sharpen the ask."


def _weighted_avg(
    reactions: List[PersonaReaction],
    personas: List[AudiencePersona],
    attr: str,
) -> float:
    weighted_total = 0.0
    for reaction, persona in zip(reactions, personas):
        weighted_total += getattr(reaction, attr) * (persona.share_pct / 100)
    return weighted_total


def _ensure_range(name: str, value: float, low: float, high: float) -> None:
    if value < low or value > high:
        raise ValueError(f"{name} must be between {low} and {high}")


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
