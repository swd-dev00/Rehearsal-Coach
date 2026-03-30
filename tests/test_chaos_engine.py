import unittest

from src.rehearsal_coach.chaos_engine import (
    ChaosEngine,
    PerformanceSnapshot,
    RecoverySnapshot,
    ResilienceScorer,
)


class ChaosEngineTests(unittest.TestCase):
    def test_triggers_time_compression_when_too_safe(self):
        engine = ChaosEngine(cooldown_sec=60)
        snapshot = PerformanceSnapshot(
            timestamp_sec=120,
            eye_contact_pct=85,
            speaking_wpm=140,
            tone_variance=0.6,
            filler_words_per_min=2,
            jargon_density_pct=8,
            confidence_score=0.9,
            engagement_score=0.7,
            claim_without_evidence_count=0,
            slide_dependency_pct=10,
        )
        event = engine.inject_if_needed(snapshot)
        self.assertIsNotNone(event)
        self.assertEqual(event.key, "time_compression")

    def test_cooldown_blocks_back_to_back_events(self):
        engine = ChaosEngine(cooldown_sec=60)
        first = PerformanceSnapshot(
            timestamp_sec=120,
            eye_contact_pct=85,
            speaking_wpm=140,
            tone_variance=0.6,
            filler_words_per_min=2,
            jargon_density_pct=8,
            confidence_score=0.9,
            engagement_score=0.7,
            claim_without_evidence_count=0,
            slide_dependency_pct=10,
        )
        second = PerformanceSnapshot(
            timestamp_sec=150,
            eye_contact_pct=85,
            speaking_wpm=140,
            tone_variance=0.6,
            filler_words_per_min=12,
            jargon_density_pct=22,
            confidence_score=0.9,
            engagement_score=0.7,
            claim_without_evidence_count=3,
            slide_dependency_pct=10,
        )
        self.assertIsNotNone(engine.inject_if_needed(first))
        self.assertIsNone(engine.inject_if_needed(second))


class ResilienceScorerTests(unittest.TestCase):
    def test_bonus_for_fast_recovery(self):
        recovery = RecoverySnapshot(
            recovery_seconds=2.5,
            message_integrity=4,
            language_control=4,
            presence_stability=4,
            decision_clarity=4,
        )
        score = ResilienceScorer.score(recovery)
        self.assertGreaterEqual(score, 85.0)

    def test_penalty_for_slow_recovery(self):
        recovery = RecoverySnapshot(
            recovery_seconds=18,
            message_integrity=5,
            language_control=5,
            presence_stability=5,
            decision_clarity=5,
        )
        score = ResilienceScorer.score(recovery)
        self.assertLess(score, 100.0)


if __name__ == "__main__":
    unittest.main()
