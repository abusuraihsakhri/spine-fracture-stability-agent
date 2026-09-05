# Spine Fracture Stability Agent

> **Domain:** Diagnostic Radiology & Medical Imaging AI
> **Reference Guidelines:** TLICS (Thoracolumbar Injury Classification and Severity), SLIC (Subaxial Cervical Spine Injury Classification), ACR RADS & Fleischner Society

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## What It Does

**Spine Fracture Stability Agent** is an analytical platform implementing TLICS & Subaxial Cervical Spine Injury Staging. It evaluates thoracolumbar and cervical trauma CTs across three dimensions: morphology, posterior ligamentous complex (PLC) integrity, and neurologic status to support surgical decision-making.

---

## Key Capabilities

### Core Evaluation Engines

- **MorphologyClassifierAgent** — Evaluates primary metric against clinical baseline thresholds
- **LigamentousIntegrityAgent** — Assesses secondary kinetics and STAT escalation triggers
- **TLICSCompositeScorerAgent** — Detects biomarker and phenotypic discordance
- **SpineCoordinator** — Executive coordinator aggregating multi-agent consensus

### Enterprise Security

- **Zero-PHI Outbound Interceptor:** AST and regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers
- **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation
- **Air-Gapped LLM Reasoning Adapter:** Integration for local Ollama, Claude, OpenAI, and deterministic mocks
- **Prometheus Telemetry:** Operational metrics exposed at `/metrics`

---

## Installation

```bash
# Clone repository
git clone https://github.com/abusuraihsakhri/spine-fracture-stability-agent.git
cd spine-fracture-stability-agent

# Install dependencies
pip install fastapi uvicorn pydantic pytest

# Or install as package
pip install -e .
```

---

## Usage

### CLI — Single Case Audit

```bash
python cli.py audit --task-id CASE-001 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### CLI — Batch CSV Processing

```bash
python cli.py batch -i sample.csv -o results.csv
```

### CLI — Query Supervisor

```bash
python cli.py chat "What is the system status?"
```

### CLI — Verify Audit Trail

```bash
python cli.py verify-audit
```

### REST API Server

```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |
| POST | `/api/audit` | Submit case for evaluation |
| POST | `/api/chat` | Query supervisory assistant |
| GET | `/api/audit/logs` | Retrieve HMAC audit trail |

---

## Input Data Schema

### Audit Payload

| Field | Type | Description | Required |
|:------|:-----|:------------|:---------|
| `task_id` | string | Unique case identifier | Yes |
| `target_identifier` | string | Target or specimen key | Yes |
| `primary_metric` | float | Primary measurement | Yes |
| `secondary_metric` | float | Secondary kinetic index | No (default: 0.0) |
| `status_descriptor` | string | Status code (e.g., NOMINAL, DISCORDANT_ANOMALY) | No (default: NOMINAL) |
| `is_critical_flag` | boolean | Emergency escalation trigger | No (default: false) |

### CSV Batch Format

```csv
task_id,target_identifier,primary_metric,secondary_metric,status_descriptor,is_critical_flag
CASE-001,SYNTH-01,25.4,14.2,DISCORDANT,true
CASE-002,SYNTH-02,12.0,4.1,NORMAL,false
```

---

## Testing

```bash
# Run full test suite
pytest -v

# Run with coverage
pytest -v --cov=agents --cov=spine_stability --cov=enrichment
```

---

## Container Deployment

```bash
docker build -t spine-fracture-stability-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=$(openssl rand -hex 32) spine-fracture-stability-agent
```

### Docker Compose

```bash
docker-compose up -d
```

---

## Security Configuration

| Environment Variable | Description | Required |
|:---------------------|:------------|:---------|
| `AUDIT_SECRET_KEY` | HMAC-SHA256 signing key for audit trail | No (random key generated if unset) |
| `MODEL_PROVIDER` | LLM provider: mock, ollama, claude, openai | No (default: mock) |

**Important:** For production deployments, always set `AUDIT_SECRET_KEY` to a cryptographically secure random value. Without it, a random key is generated per process, which prevents audit trail verification across restarts.

---

## Architecture

```
spine-fracture-stability-agent/
├── agents/                  # Enterprise agent modules
│   ├── base.py             # PHI guard, HMAC audit, security
│   ├── models.py           # Pydantic schemas
│   ├── supervisor.py       # Master orchestrator
│   ├── workers.py          # Specialized evaluation workers
│   ├── api.py              # FastAPI REST server
│   ├── llm_factory.py      # LLM provider factory
│   ├── learning.py         # Bayesian calibration engine
│   ├── metrics.py          # Prometheus metrics collector
│   └── streamer.py         # WebSocket telemetry broadcaster
├── spine_fracture_stability_agent/  # Alternative package
├── cli.py                  # CLI entry point
├── spine_stability.py      # Core evaluation engine
├── enrichment.py           # Enrichment analytics suite
├── simulator.py            # High-throughput stress tester
└── tests/                  # Test suite
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
