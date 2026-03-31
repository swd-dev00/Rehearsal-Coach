import unittest

from src.rehearsal_coach.simulated_audience import (
    AudiencePersona,
    AudienceSimulator,
    SimulationInput,
)


class AudienceSimulatorTests(unittest.TestCase):
    def setUp(self):
        self.personas = [
            AudiencePersona(
                name="Gen Z",
                share_pct=50,
                clarity_weight=0.3,
                pacing_weight=0.2,
                evidence_weight=0.1,
                engagement_weight=0.4,
                skepticism=0.4,
            ),
            AudiencePersona(
                name="Executives",
                share_pct=50,
                clarity_weight=0.25,
                pacing_weight=0.15,
                evidence_weight=0.35,
                engagement_weight=0.25,
                skepticism=0.75,
            ),
        ]

    def test_simulation_returns_weighted_report(self):
        simulator = AudienceSimulator(self.personas, seed=42)
        report = simulator.simulate(
            SimulationInput(
                clarity_score=0.82,
                pacing_score=0.7,
                evidence_score=0.6,
                engagement_score=0.78,
            )
        )

        self.assertGreaterEqual(report.weighted_sentiment, 0)
        self.assertLessEqual(report.weighted_sentiment, 1)
        self.assertEqual(len(report.reactions), 2)
        self.assertEqual(report.top_risk, "evidence_deficit")

    def test_persona_shares_must_sum_to_100(self):
        with self.assertRaises(ValueError):
            AudienceSimulator(
                [
                    AudiencePersona(
                        name="A",
                        share_pct=70,
                        clarity_weight=0.3,
                        pacing_weight=0.2,
                        evidence_weight=0.2,
                        engagement_weight=0.3,
                        skepticism=0.5,
                    ),
                    AudiencePersona(
                        name="B",
                        share_pct=20,
                        clarity_weight=0.3,
                        pacing_weight=0.2,
                        evidence_weight=0.2,
                        engagement_weight=0.3,
                        skepticism=0.5,
                    ),
                ]
            )


if __name__ == "__main__":
    unittest.main()
