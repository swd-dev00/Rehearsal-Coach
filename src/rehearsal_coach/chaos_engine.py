"""Rule-based chaos event injection and resilience scoring for rehearsals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class PerformanceSnapshot:
    timestamp_sec: int
    eye_contact_pct: float
    speaking_wpm: int
    tone_variance: float
    filler_words_per_min: float
    jargon_density_pct: float
    confidence_score: float
    engagement_score: float
    claim_without_evidence_count: int
    slide_dependency_pct: float

    def __post_init__(self) -> None:
        _ensure_non_negative("timestamp_sec", self.timestamp_sec)
        _ensure_range("eye_contact_pct", self.eye_contact_pct, 0, 100)
        _ensure_non_negative("speaking_wpm", self.speaking_wpm)
        _ensure_non_negative("tone_variance", self.tone_variance)
        _ensure_non_negative("filler_words_per_min", self.filler_words_per_min)
        _ensure_range("jargon_density_pct", self.jargon_density_pct, 0, 100)
        _ensure_range("confidence_score", self.confidence_score, 0, 1)
        _ensure_range("engagement_score", self.engagement_score, 0, 1)
        _ensure_non_negative("claim_without_evidence_count", self.claim_without_evidence_count)
        _ensure_range("slide_dependency_pct", self.slide_dependency_pct, 0, 100)


@dataclass(frozen=True)
class ChaosEvent:
    key: str
    severity: str
    script: str
    recovery_window_sec: int
    score_weight: float


@dataclass(frozen=True)
class RecoverySnapshot:
    recovery_seconds: float
    message_integrity: int  # 0-5
    language_control: int  # 0-5
    presence_stability: int  # 0-5
    decision_clarity: int  # 0-5

    def __post_init__(self) -> None:
        _ensure_non_negative("recovery_seconds", self.recovery_seconds)
        for field_name, value in [
            ("message_integrity", self.message_integrity),
            ("language_control", self.language_control),
            ("presence_stability", self.presence_stability),
            ("decision_clarity", self.decision_clarity),
        ]:
            _ensure_range(field_name, value, 0, 5)


@dataclass(frozen=True)
class ActiveEvent:
    event: ChaosEvent
    started_at_sec: int

    @property
    def ends_at_sec(self) -> int:
        return self.started_at_sec + self.event.recovery_window_sec


class ChaosEngine:
    """Injects pressure events when user is too comfortable or vulnerable."""

    def __init__(
        self,
        cooldown_sec: int = 60,
        max_events_per_session: int = 6,
        max_concurrent_events: int = 2,
    ) -> None:
        _ensure_non_negative("cooldown_sec", cooldown_sec)
        _ensure_non_negative("max_events_per_session", max_events_per_session)
        _ensure_non_negative("max_concurrent_events", max_concurrent_events)

        self.cooldown_sec = cooldown_sec
        self.max_events_per_session = max_events_per_session
        self.max_concurrent_events = max_concurrent_events
        self._event_log: List[tuple[int, ChaosEvent]] = []
        self._active_events: List[ActiveEvent] = []

    @property
    def event_count(self) -> int:
        return len(self._event_log)

    @property
    def active_event_count(self) -> int:
        return len(self._active_events)

    def inject_if_needed(self, snapshot: PerformanceSnapshot) -> Optional[ChaosEvent]:
        self._expire_events(snapshot.timestamp_sec)

        if self.event_count >= self.max_events_per_session:
            return None

        if self.active_event_count >= self.max_concurrent_events:
            return None

        if self._is_cooldown(snapshot.timestamp_sec):
            return None

        event = self._select_event(snapshot)
        if event:
            self._event_log.append((snapshot.timestamp_sec, event))
            self._active_events.append(ActiveEvent(event=event, started_at_sec=snapshot.timestamp_sec))
        return event

    def resolve_event(self, key: str) -> bool:
        """Manually resolve an active event by key; returns True if removed."""
        for idx, active in enumerate(self._active_events):
            if active.event.key == key:
                self._active_events.pop(idx)
                return True
        return False

    def _expire_events(self, now_sec: int) -> None:
        self._active_events = [e for e in self._active_events if e.ends_at_sec > now_sec]

    def _is_cooldown(self, now_sec: int) -> bool:
        if not self._event_log:
            return False
        last_time, _ = self._event_log[-1]
        return (now_sec - last_time) < self.cooldown_sec

    def _select_event(self, s: PerformanceSnapshot) -> Optional[ChaosEvent]:
        # Priority order: safety drift, evidence gap, clarity collapse, over-reliance, low engagement.
        if s.confidence_score > 0.85 and s.eye_contact_pct > 80 and s.timestamp_sec > 90:
            return ChaosEvent(
                key="time_compression",
                severity="high",
                script="Update: agenda shifted. You have 60 seconds to close with a clear ask.",
                recovery_window_sec=60,
                score_weight=1.2,
            )

        if s.claim_without_evidence_count >= 2:
            return ChaosEvent(
                key="hostile_challenge",
                severity="high",
                script="I don't buy that. Give one specific proof point in 20 seconds.",
                recovery_window_sec=20,
                score_weight=1.1,
            )

        if s.jargon_density_pct > 18 or s.filler_words_per_min > 10:
            return ChaosEvent(
                key="confusion_spike",
                severity="medium",
                script="Audience signal: unclear. Reframe this in plain language now.",
                recovery_window_sec=30,
                score_weight=1.0,
            )

        if s.slide_dependency_pct > 45:
            return ChaosEvent(
                key="slide_failure",
                severity="high",
                script="We lost your deck. Continue off-book. Audience is still with you.",
                recovery_window_sec=45,
                score_weight=1.3,
            )

        if s.engagement_score < 0.45:
            return ChaosEvent(
                key="executive_cut_in",
                severity="medium",
                script="I'm joining late. Give me the full case in 30 seconds.",
                recovery_window_sec=30,
                score_weight=1.0,
            )

        return None


class ResilienceScorer:
    """Computes a 0-100 resilience score from recovery behavior."""

    @staticmethod
    def score(r: RecoverySnapshot) -> float:
        recovery_speed_score = ResilienceScorer._recovery_speed_score(r.recovery_seconds)
        dimensions = [
            recovery_speed_score,
            r.message_integrity,
            r.language_control,
            r.presence_stability,
            r.decision_clarity,
        ]
        normalized = sum(dimensions) / 25
        score = round(normalized * 100, 1)

        # Bonus/penalty rules
        if r.recovery_seconds <= 3:
            score = min(100.0, score + 5.0)
        if r.recovery_seconds > 15:
            score = max(0.0, score - 5.0)

        return round(score, 1)

    @staticmethod
    def _recovery_speed_score(seconds: float) -> int:
        if seconds <= 3:
            return 5
        if seconds <= 5:
            return 4
        if seconds <= 8:
            return 3
        if seconds <= 12:
            return 2
        if seconds <= 15:
            return 1
        return 0


def _ensure_non_negative(name: str, value: float) -> None:
    if value < 0:
        raise ValueError(f"{name} must be >= 0")


def _ensure_range(name: str, value: float, low: float, high: float) -> None:
    if value < low or value > high:
        raise ValueError(f"{name} must be between {low} and {high}")
