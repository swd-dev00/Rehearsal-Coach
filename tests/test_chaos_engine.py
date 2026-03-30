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

    def test_concurrency_limit_blocks_new_events_while_active(self):
        engine = ChaosEngine(cooldown_sec=0, max_concurrent_events=1)
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
            timestamp_sec=121,
            eye_contact_pct=70,
            speaking_wpm=140,
            tone_variance=0.6,
            filler_words_per_min=12,
            jargon_density_pct=22,
            confidence_score=0.8,
            engagement_score=0.7,
            claim_without_evidence_count=3,
            slide_dependency_pct=10,
        )
        self.assertIsNotNone(engine.inject_if_needed(first))
        self.assertIsNone(engine.inject_if_needed(second))

    def test_resolve_event_allows_new_injection(self):
        engine = ChaosEngine(cooldown_sec=0, max_concurrent_events=1)
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
        follow_up = PerformanceSnapshot(
            timestamp_sec=121,
            eye_contact_pct=70,
            speaking_wpm=140,
            tone_variance=0.6,
            filler_words_per_min=12,
            jargon_density_pct=22,
            confidence_score=0.8,
            engagement_score=0.7,
            claim_without_evidence_count=3,
            slide_dependency_pct=10,
        )
        first_event = engine.inject_if_needed(first)
        self.assertTrue(engine.resolve_event(first_event.key))
        second_event = engine.inject_if_needed(follow_up)
        self.assertIsNotNone(second_event)
        self.assertEqual(second_event.key, "hostile_challenge")


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


class ValidationTests(unittest.TestCase):
    def test_snapshot_rejects_out_of_range_fields(self):
        with self.assertRaises(ValueError):
            PerformanceSnapshot(
                timestamp_sec=1,
                eye_contact_pct=101,
                speaking_wpm=140,
                tone_variance=0.5,
                filler_words_per_min=1,
                jargon_density_pct=10,
                confidence_score=0.8,
                engagement_score=0.6,
                claim_without_evidence_count=0,
                slide_dependency_pct=20,
            )

    def test_recovery_rejects_negative_seconds(self):
        with self.assertRaises(ValueError):
            RecoverySnapshot(
                recovery_seconds=-1,
                message_integrity=4,
                language_control=4,
                presence_stability=4,
                decision_clarity=4,
            )


if __name__ == "__main__":
    unittest.main()
