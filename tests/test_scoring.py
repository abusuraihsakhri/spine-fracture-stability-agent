"""Reference-case and adversarial tests for scoring and audit integrity."""
import pytest

from spine_fracture_stability_agent.scoring import score_case
from agents.base import AuditTrail


@pytest.mark.parametrize(
    "scale,morphology,ligament,neurologic,modifier,total,band",
    [
        ("TLICS", "compression", "intact", "intact", False, 1, "nonoperative_favored"),
        ("TLICS", "burst", "indeterminate", "intact", False, 4, "equivocal"),
        ("TLICS", "distraction", "disrupted", "incomplete_cord", False, 10, "operative_favored"),
        ("TLICS", "translation_rotation", "intact", "nerve_root", False, 5, "operative_favored"),
        ("SLIC", "burst", "intact", "intact", False, 2, "nonoperative_favored"),
        ("SLIC", "compression", "indeterminate", "complete_cord", False, 4, "equivocal"),
        ("SLIC", "distraction", "disrupted", "incomplete_cord", True, 9, "operative_favored"),
        ("SLIC", "translation_rotation", "intact", "intact", False, 4, "equivocal"),
    ],
)
def test_reference_cases(scale, morphology, ligament, neurologic, modifier, total, band):
    result = score_case(scale, morphology, ligament, neurologic, modifier)
    assert result["total"] == total
    assert result["band"] == band
    assert sum(result["points"].values()) == total


@pytest.mark.parametrize(
    "kwargs",
    [
        {"scale": "OTHER", "morphology": "burst", "ligament": "intact", "neurologic": "intact"},
        {"scale": "TLICS", "morphology": "invented", "ligament": "intact", "neurologic": "intact"},
        {"scale": "SLIC", "morphology": "none", "ligament": "intact", "neurologic": "cauda_equina"},
        {"scale": "TLICS", "morphology": "burst", "ligament": "intact", "neurologic": "intact", "ongoing_compression": True},
        {"scale": "SLIC", "morphology": "burst", "ligament": "intact", "neurologic": "intact", "ongoing_compression": True},
        {"scale": "SLIC", "morphology": "burst", "ligament": "intact", "neurologic": "nerve_root", "ongoing_compression": 1},
    ],
)
def test_invalid_categories_are_rejected(kwargs):
    with pytest.raises(ValueError):
        score_case(**kwargs)


def test_tampering_with_signed_field_is_detected():
    trail = AuditTrail("unit-test-key")
    trail.log("worker", "supervisor", "EVALUATED", {"result": "initial"})
    trail.log("worker", "supervisor", "EVALUATED", {"result": "second"})
    assert trail.verify_integrity()
    trail.logs[0]["event_type"] = "FORGED"
    assert not trail.verify_integrity()


def test_tampering_with_final_signature_is_detected():
    trail = AuditTrail("unit-test-key")
    trail.log("worker", "supervisor", "EVALUATED", {"ok": True})
    trail.logs[-1]["current_hash"] = "f" * 64
    assert not trail.verify_integrity()


def test_get_trail_does_not_expose_live_mutable_entries():
    trail = AuditTrail("unit-test-key")
    trail.log("worker", "supervisor", "EVALUATED", {"ok": True})
    snapshot = trail.get_trail()
    snapshot[0]["event_type"] = "FORGED"
    snapshot.clear()
    assert trail.verify_integrity()
    assert len(trail.get_trail()) == 1
