"""Security regression tests for legacy compatibility APIs."""
import math
import pytest
from pydantic import ValidationError

from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from agents.llm_factory import LLMFactory
from agents.base import SecurityException
from spine_stability import LigamentousIntegrityAgent


@pytest.mark.parametrize("bad_value", [math.nan, math.inf, -math.inf])
def test_nonfinite_metrics_are_not_valid_payloads(bad_value):
    with pytest.raises(ValidationError):
        SystemTaskPayload(
            task_id="T-1", target_identifier="SYNTHETIC-1", primary_metric=bad_value,
        )
    with pytest.raises(ValidationError):
        SystemTaskPayload(
            task_id="T-1", target_identifier="SYNTHETIC-1",
            primary_metric=1.0, secondary_metric=bad_value,
        )


def test_phi_guard_checks_nested_metadata_not_just_top_level_identifiers():
    task = SystemTaskPayload(
        task_id="T-1", target_identifier="SYNTHETIC-1", primary_metric=1,
        attributes={"annotation": {"contact": "patient@example.org"}},
    )
    with pytest.raises(SecurityException):
        SystemSupervisor().process_task(task)


def test_unimplemented_model_providers_fail_explicitly():
    with pytest.raises(ValueError, match="not implemented"):
        LLMFactory.create("openai")


def test_mock_does_not_claim_analysis_or_echo_input():
    response = LLMFactory.create("mock").invoke("synthetic detail 73423")
    assert "synthetic detail" not in response
    assert "No clinical analysis" in response


def test_legacy_batch_false_flag_is_not_truthy():
    assert LigamentousIntegrityAgent().evaluate({
        "critical_flag": "False",
        "metric_secondary": 0.0,
    }) == []
