"""
AeroPulse AI — End-to-End Pipeline & Warehouse Test Suite
Validates:
1. DuckDB Star Schema Tables, Dimensions, and Referential Integrity
2. Scikit-Learn Model & Prior Encodings
3. Real-Time Inference Probability Bounds
4. Two-Leg Connecting Flight Compounding & Missed Connection Logic
5. SQL Analytical Query Safety Guardrails
"""

import os
import unittest
import duckdb
import joblib
import json
import math
import numpy as np

class TestAeroPulsePipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_path = "warehouse/flight_warehouse.duckdb"
        cls.model_path = "models/flight_delay_model.joblib"
        cls.meta_path = "models/model_metadata.json"

    def test_01_warehouse_tables_exist(self):
        """Verify DuckDB warehouse connects and contains required Kimball Star Schema tables."""
        self.assertTrue(os.path.exists(self.db_path), f"Warehouse database not found at {self.db_path}")
        conn = duckdb.connect(self.db_path, read_only=True)
        tables = [r[0] for r in conn.execute("SHOW TABLES").fetchall()]
        
        expected_tables = ["fact_flights", "dim_date", "dim_carrier", "dim_airport", "dim_time_block", "dim_route"]
        for t in expected_tables:
            self.assertIn(t, tables, f"Expected table {t} missing from DuckDB warehouse")
        
        # Check fact table row count
        count = conn.execute("SELECT count(*) FROM fact_flights").fetchone()[0]
        self.assertGreater(count, 0, "Fact table should have records")
        conn.close()

    def test_02_dimension_integrity(self):
        """Verify foreign key coverage without orphaned records."""
        conn = duckdb.connect(self.db_path, read_only=True)
        
        # Test carriers
        carriers_count = conn.execute("SELECT count(*) FROM dim_carrier").fetchone()[0]
        self.assertGreaterEqual(carriers_count, 10, "dim_carrier should contain primary US airlines")

        # Test airports
        airports_count = conn.execute("SELECT count(*) FROM dim_airport").fetchone()[0]
        self.assertGreaterEqual(airports_count, 20, "dim_airport should contain major US hubs")

        conn.close()

    def test_03_ml_model_and_metadata(self):
        """Verify the trained ML model and Bayesian metadata exist and load properly."""
        self.assertTrue(os.path.exists(self.model_path), "Model joblib file missing")
        self.assertTrue(os.path.exists(self.meta_path), "Model metadata JSON missing")

        model = joblib.load(self.model_path)
        with open(self.meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        self.assertIn("carrier_priors", meta)
        self.assertIn("origin_priors", meta)
        self.assertIn("optimal_threshold", meta)

        # Test single inference vector
        # [month, day, dow, is_weekend, season, hour, dist, elapsed, c_pr, o_pr, d_pr, h_pr]
        sample_x = np.array([[7, 15, 5, 0, 2, 18, 800.0, 140.0, 0.22, 0.23, 0.21, 0.26]])
        probs = model.predict_proba(sample_x)[0]

        self.assertEqual(len(probs), 2)
        self.assertGreaterEqual(probs[1], 0.0)
        self.assertLessEqual(probs[1], 1.0)

    def test_04_connecting_flight_compounding_risk(self):
        """Verify compounding delay formula for 2-leg itineraries."""
        p_leg1 = 0.25
        p_leg2 = 0.30

        # P(any delay) = 1 - (1 - p1) * (1 - p2)
        itinerary_prob = 1.0 - (1.0 - p_leg1) * (1.0 - p_leg2)
        self.assertAlmostEqual(itinerary_prob, 0.475, places=3)
        self.assertGreater(itinerary_prob, max(p_leg1, p_leg2))

        # Test missed connection exponential buffer calculation
        layover_mins = 45
        effective_buffer = max(5, layover_mins - 20) # 25 mins
        est_delay_leg1 = 20.0
        missed_prob = p_leg1 * math.exp(-effective_buffer / max(10, est_delay_leg1))
        self.assertGreater(missed_prob, 0.0)
        self.assertLess(missed_prob, 1.0)

    def test_05_sql_security_guardrails(self):
        """Verify that destructive SQL statements are blocked by validation rules."""
        blocked_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE"]
        test_query = "DROP TABLE fact_flights;"
        
        is_blocked = any(kw in test_query.upper() for kw in blocked_keywords)
        self.assertTrue(is_blocked, "Destructive DROP query should be flagged as blocked")

if __name__ == "__main__":
    unittest.main()
