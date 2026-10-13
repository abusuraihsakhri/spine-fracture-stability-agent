"""
FastAPI REST Application & Webhooks for SpineStability Sentinel: TLICS & Subaxial Cervical Spine Injury Staging Agent.
"""
from typing import Dict, Any, Optional
from .models import ClinicalCasePayload
from .agents import SpineCoordinator

coordinator = SpineCoordinator()

def create_app():
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel
        from .scoring import score_case

        app = FastAPI(
            title="SpineStability Sentinel: TLICS & Subaxial Cervical Spine Injury Staging Agent",
            description="Evaluates thoracolumbar (TLICS) and cervical (SLIC) trauma CTs: morphology, posterior ligamentous complex (PLC), and neurologic status for surgery.",
            version="2.0.0-PRO",
        )

        class AuditRequest(BaseModel):
            case_id: str = "CASE-2026-001"
            patient_synthetic_id: str = "SYNTH-PT-881"
            primary_metric: float = 24.5
            secondary_metric: float = 14.0
            status_flag: str = "DISCORDANT"
            is_stat: bool = True
            clinical_notes: str = ""
            biomarkers: Dict[str, Any] = {}

        class ScoreRequest(BaseModel):
            scale: str
            morphology: str
            ligament: str
            neurologic: str
            ongoing_compression: bool = False

        class ChatRequest(BaseModel):
            query: str

        @app.get("/health")
        def health():
            return {"status": "HEALTHY", "system": "spine-fracture-stability-agent", "domain": "Musculoskeletal Imaging", "version": "2.0.0-PRO"}

        @app.post("/api/audit")
        def api_audit(req: AuditRequest):
            payload = ClinicalCasePayload(
                case_id=req.case_id,
                patient_synthetic_id=req.patient_synthetic_id,
                primary_metric=req.primary_metric,
                secondary_metric=req.secondary_metric,
                status_flag=req.status_flag,
                is_stat=req.is_stat,
                clinical_notes=req.clinical_notes,
                biomarkers=req.biomarkers,
            )
            return coordinator.process_case(payload)

        @app.post("/api/score")
        def api_score(req: ScoreRequest):
            try:
                return score_case(**req.model_dump())
            except ValueError as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc

        @app.post("/api/chat")
        def api_chat(req: ChatRequest):
            return {"response": coordinator.query_supervisory_chat(req.query)}

        return app
    except ImportError:
        return None
