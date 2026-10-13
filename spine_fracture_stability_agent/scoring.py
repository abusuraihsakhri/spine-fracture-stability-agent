"""Educational TLICS and SLIC point calculators.

Points and decision bands follow the published classification schemes, not the
legacy generic metric thresholds elsewhere in this repository. These scoring
systems support specialist assessment; they do not establish spinal stability
or replace clinical evaluation.
"""
from typing import Any, Dict

SCALES = {
    "TLICS": {
        "morphology": {
            "none": 0, "compression": 1, "burst": 2,
            "translation_rotation": 3, "distraction": 4,
        },
        "ligament": {"intact": 0, "indeterminate": 2, "disrupted": 3},
        "neurologic": {
            "intact": 0, "nerve_root": 2, "complete_cord": 2,
            "incomplete_cord": 3, "cauda_equina": 3,
        },
    },
    "SLIC": {
        "morphology": {
            "none": 0, "compression": 1, "burst": 2,
            "distraction": 3, "translation_rotation": 4,
        },
        "ligament": {"intact": 0, "indeterminate": 1, "disrupted": 2},
        "neurologic": {
            "intact": 0, "nerve_root": 1, "complete_cord": 2,
            "incomplete_cord": 3,
        },
    },
}

REFERENCES = {
    "TLICS": "https://pmc.ncbi.nlm.nih.gov/articles/PMC2779435/",
    "SLIC": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3032869/",
}


def score_case(
    scale: str,
    morphology: str,
    ligament: str,
    neurologic: str,
    ongoing_compression: bool = False,
) -> Dict[str, Any]:
    """Score one injury level using an explicit, mutually exclusive category.

    For SLIC only, an additional point may be assigned for ongoing spinal
    cord compression in the presence of a neurologic deficit.
    """
    if not isinstance(scale, str):
        raise ValueError("scale must be TLICS or SLIC")
    scale = scale.upper()
    if scale not in SCALES:
        raise ValueError("scale must be TLICS or SLIC")
    if not isinstance(ongoing_compression, bool):
        raise ValueError("ongoing_compression must be a boolean")
    if scale == "TLICS" and ongoing_compression:
        raise ValueError("ongoing_compression modifier applies only to SLIC")
    if ongoing_compression and neurologic == "intact":
        raise ValueError("ongoing cord compression modifier requires neurologic deficit")

    points = {}
    for group, selection in (
        ("morphology", morphology),
        ("ligament", ligament),
        ("neurologic", neurologic),
    ):
        if not isinstance(selection, str) or selection not in SCALES[scale][group]:
            allowed = ", ".join(SCALES[scale][group])
            raise ValueError(f"Invalid {group} for {scale}. Allowed: {allowed}")
        points[group] = SCALES[scale][group][selection]

    points["ongoing_compression"] = int(ongoing_compression)
    total = sum(points.values())
    if total <= 3:
        band = "nonoperative_favored"
        interpretation = "Classification framework generally favors nonoperative management."
    elif total == 4:
        band = "equivocal"
        interpretation = "Borderline score: treatment choice requires specialist judgment."
    else:
        band = "operative_favored"
        interpretation = "Classification framework generally favors operative evaluation."

    return {
        "scale": scale,
        "categories": {
            "morphology": morphology,
            "ligament": ligament,
            "neurologic": neurologic,
            "ongoing_compression": ongoing_compression,
        },
        "points": points,
        "total": total,
        "band": band,
        "interpretation": interpretation,
        "reference": REFERENCES[scale],
        "disclaimer": (
            "Educational decision support only. Scoring does not establish spinal "
            "stability or substitute for image review, neurologic examination, "
            "or consultation with a spine specialist."
        ),
    }
