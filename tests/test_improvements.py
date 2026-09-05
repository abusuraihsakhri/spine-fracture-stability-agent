"""
Focused tests for security, reliability, and code quality improvements.
"""
import os
import sys
import tempfile
import csv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import AuditTrail, PHIGuard, SecurityException, assert_no_phi
from cli import main as cli_main
from enrichment import ThresholdEnrichmentEngine, EnrichmentResult


class TestAuditTrailSecurity:
    """Tests for HMAC audit trail security improvements."""

    def test_random_key_generated_when_no_env_set(self):
        """When no key is provided and no env var set, a random key should be generated."""
        # Ensure env var is not set
        original = os.environ.pop("AUDIT_SECRET_KEY", None)
        try:
            trail = AuditTrail()
            assert len(trail.secret_key) == 64  # 32 bytes hex encoded = 64 chars
        finally:
            if original is not None:
                os.environ["AUDIT_SECRET_KEY"] = original

    def test_different_instances_get_different_keys(self):
        """Two instances without explicit key should have different keys."""
        original = os.environ.pop("AUDIT_SECRET_KEY", None)
        try:
            trail1 = AuditTrail()
            trail2 = AuditTrail()
            assert trail1.secret_key != trail2.secret_key
        finally:
            if original is not None:
                os.environ["AUDIT_SECRET_KEY"] = original

    def test_explicit_key_is_used(self):
        """When a key is provided explicitly, it should be used."""
        trail = AuditTrail(secret_key="my-test-key")
        assert trail.secret_key == b"my-test-key"

    def test_env_var_key_is_used(self):
        """When AUDIT_SECRET_KEY env var is set, it should be used."""
        os.environ["AUDIT_SECRET_KEY"] = "env-based-key"
        try:
            trail = AuditTrail()
            assert trail.secret_key == b"env-based-key"
        finally:
            del os.environ["AUDIT_SECRET_KEY"]

    def test_audit_trail_integrity_with_random_key(self):
        """Audit trail should maintain integrity even with random keys."""
        trail = AuditTrail()
        trail.log("test", "tier", "EVENT", {"data": "value1"})
        trail.log("test", "tier", "EVENT", {"data": "value2"})
        assert trail.verify_integrity() is True
        assert len(trail.get_trail()) == 2


class TestPHIGuardEnhancements:
    """Tests for PHI guard functionality."""

    def test_clean_text_passes(self):
        PHIGuard.assert_no_phi("Analytical specimen KEY-001 optimal")
        PHIGuard.assert_no_phi("Metric value 24.5 within normal range")

    def test_mrn_pattern_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive")

    def test_ssn_pattern_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN: 123-45-6789 for patient record")

    def test_phone_pattern_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Contact patient at 555-123-4567")

    def test_email_pattern_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Send results to doctor@hospital.org")

    def test_redact_phi_works(self):
        result = PHIGuard.redact_phi("Patient MRN-12345678 and SSN 123-45-6789")
        assert "REDACTED_IDENTIFIER" in result
        assert "MRN" not in result
        assert "123-45-6789" not in result

    def test_empty_text_passes(self):
        PHIGuard.assert_no_phi("")

    def test_none_text_passes(self):
        PHIGuard.assert_no_phi(None)


class TestBatchErrorHandling:
    """Tests for CLI batch processing error handling."""

    def test_batch_missing_file_returns_error(self):
        """Batch with non-existent file should return error code."""
        result = cli_main(["batch", "-i", "nonexistent_file_xyz.csv"])
        assert result == 1

    def test_batch_malformed_csv_handled_gracefully(self):
        """Batch with malformed CSV data should skip bad rows."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write("task_id,target_identifier,primary_metric,secondary_metric,status_descriptor,is_critical_flag\n")
            f.write("T1,TARGET-1,25.0,10.0,NOMINAL,false\n")
            f.write("T2,TARGET-2,INVALID,10.0,NOMINAL,false\n")  # Bad primary_metric
            f.write("T3,TARGET-3,15.0,5.0,NOMINAL,false\n")
            temp_path = f.name

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as out_f:
                output_path = out_f.name

            result = cli_main(["batch", "-i", temp_path, "-o", output_path])
            assert result == 0

            with open(output_path, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                # Should have processed 2 valid rows (T1 and T3), skipping T2
                assert len(rows) == 2
                assert rows[0]["task_id"] == "T1"
                assert rows[1]["task_id"] == "T3"
        finally:
            os.unlink(temp_path)
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_batch_valid_csv_succeeds(self):
        """Batch with valid CSV should process all rows."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write("task_id,target_identifier,primary_metric,secondary_metric,status_descriptor,is_critical_flag\n")
            f.write("T1,TARGET-1,10.0,5.0,NOMINAL,false\n")
            f.write("T2,TARGET-2,15.0,8.0,NOMINAL,false\n")
            temp_path = f.name

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as out_f:
                output_path = out_f.name

            result = cli_main(["batch", "-i", temp_path, "-o", output_path])
            assert result == 0

            with open(output_path, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 2
        finally:
            os.unlink(temp_path)
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestThresholdEnrichmentEngine:
    """Tests for the refactored enrichment engine."""

    def test_optimal_status(self):
        engine = ThresholdEnrichmentEngine("Test Feature", threshold=10.0)
        result = engine.evaluate(5.0)
        assert result.status == "OPTIMAL"
        assert result.score == 5.0
        assert len(result.alerts) == 0

    def test_warning_status(self):
        engine = ThresholdEnrichmentEngine("Test Feature", threshold=10.0)
        result = engine.evaluate(15.0)
        assert result.status == "WARNING"
        assert len(result.alerts) == 1
        assert "Test Feature" in result.alerts[0]

    def test_critical_status(self):
        engine = ThresholdEnrichmentEngine("Test Feature", threshold=10.0)
        result = engine.evaluate(25.0)
        assert result.status == "CRITICAL_ALERT"
        assert len(result.alerts) == 1

    def test_history_tracking(self):
        engine = ThresholdEnrichmentEngine("Test Feature", threshold=10.0)
        engine.evaluate(5.0)
        engine.evaluate(15.0)
        engine.evaluate(25.0)
        assert len(engine.history) == 3

    def test_feature_name_in_result(self):
        engine = ThresholdEnrichmentEngine("Custom Feature Name", threshold=1.0)
        result = engine.evaluate(0.5)
        assert result.feature_name == "Custom Feature Name"

    def test_metrics_included(self):
        engine = ThresholdEnrichmentEngine("Test", threshold=1.0)
        result = engine.evaluate(5.0, 3.0, extra="value")
        assert result.metrics["primary"] == 5.0
        assert result.metrics["secondary"] == 3.0
        assert result.metrics["extra"] == "value"


class TestSeverityEnum:
    """Tests for proper Severity enum implementation."""

    def test_severity_is_str_enum(self):
        from spine_stability import Severity
        assert issubclass(Severity, str)

    def test_severity_values(self):
        from spine_stability import Severity
        assert Severity.INFO == "INFO"
        assert Severity.ADVISORY == "ADVISORY"
        assert Severity.WARNING == "WARNING"
        assert Severity.CRITICAL == "CRITICAL_ACTION_REQUIRED"

    def test_severity_comparison(self):
        from spine_stability import Severity
        assert Severity.WARNING == "WARNING"
        assert Severity.WARNING != "CRITICAL"
