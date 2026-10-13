# Spine Fracture Stability Agent

Reference-based **TLICS (thoracolumbar)** and **SLIC (subaxial cervical)** point calculators, with a standalone browser interface, Python CLI, and optional FastAPI endpoints.

> **Educational / research decision support only.** These scores are not an autonomous diagnosis of spinal stability or a substitute for radiologic interpretation, neurologic examination, or spine-specialist assessment. Do not enter identifiable patient information.

## Browser calculator

Open [web/index.html](web/index.html) in a current browser. Select one classification, then injury morphology, ligamentous status and neurologic status. For SLIC, a conditional +1 modifier is available for ongoing cord compression with a neurologic deficit. The page computes the total and component scores and exports a JSON summary.

The browser calculation uses **local JavaScript**, does not contact a server, and needs neither Python nor an API key. A GitHub Pages deployment workflow publishes the `web/` directory from `master` when GitHub Pages is enabled. Deployment status must be verified independently; a successful local test does not establish that the public site is live.

## Scoring and interpretation

| Scale | Components | Score bands |
| --- | --- | --- |
| TLICS | Fracture morphology (0–4), posterior ligamentous complex (0/2/3), neurologic status (0/2/3) | 0–3 generally favors nonoperative management; 4 equivocal; 5+ generally favors operative evaluation |
| SLIC | Injury morphology (0–4), discoligamentous complex (0/1/2), neurologic status (0–3), optional ongoing-compression modifier (+1) | Same decision bands |

Only the most severe relevant morphology is selected for **each injury level**. Score bands summarize the published frameworks, not treatment orders. They do not account for every clinical factor or classification reliability limitation.

The **legacy `audit`, `batch`, and `chat` interfaces** remain available for backward compatibility. Their generic numeric thresholds and mock responses **are not TLICS/SLIC calculations and have not been validated for clinical triage**.

## Installation and CLI

Python 3.9+ is required for the Python package. Python 3.10–3.12 are covered in CI.

```bash
git clone https://github.com/abusuraihsakhri/spine-fracture-stability-agent.git
cd spine-fracture-stability-agent
python -m pip install -e '.[api,dev]'
```

Calculate TLICS and SLIC reference scores:

```bash
python cli.py score --scale TLICS --morphology burst --ligament indeterminate --neurologic intact
python cli.py score --scale SLIC --morphology distraction --ligament disrupted --neurologic incomplete_cord --ongoing-compression
```

The installed console script `spine-fracture-stability-engine` also supports the `score` subcommand. Input category names are listed in [the scoring source](spine_fracture_stability_agent/scoring.py); invalid categories fail with an error rather than silently receiving a default value.

Legacy commands (generic monitoring only):

```bash
python cli.py audit --task-id TEST-01 --target SYNTH-01 --primary 28.5 --secondary 14.2 --critical
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
python cli.py chat "system status"
```

## Optional REST API

```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

API schema is available at `/docs` and `/openapi.json` while the server is running.

| Method | Path | Behavior |
| --- | --- | --- |
| POST | `/api/score` | Calculate categorical TLICS/SLIC points, without retaining the scoring request |
| POST | `/api/audit` | Run the **legacy generic threshold** assessment |
| POST | `/api/chat` | Deterministic mock response; no external inference |
| GET | `/health` | Health metadata |
| GET | `/metrics` | JSON operational counters (not Prometheus exposition format) |
| GET | `/api/audit/logs` | In-memory audit-chain metadata and integrity result |

Example score request:

```bash
curl -s http://127.0.0.1:8000/api/score \
  -H 'Content-Type: application/json' \
  -d '{"scale":"TLICS","morphology":"burst","ligament":"indeterminate","neurologic":"intact"}'
```

## Privacy and security limitations

- Browser scoring occurs locally with no uploads, cookies or persistent storage.
- Legacy server data and the audit log exist **in process memory**; do not assume durable retention, access control, or regulatory compliance. The legacy API has **no authentication**: keep it bound to a trusted interface or protect it behind an authenticated reverse proxy before deployment.
- The PHI guard uses pattern matching for *some* common identifiers. It cannot prove data are de-identified or HIPAA compliant. **Use synthetic data only**.
- Legacy audit entries form a signed HMAC-SHA256 hash chain, and verification recomputes signatures to detect changes to recorded fields. The ledger is not a persistent independent audit service. Set a strong, stable `AUDIT_SECRET_KEY` in server deployments.
- The `mock` model provider is the only implemented provider. Other names are rejected rather than silently claiming a model was used.

For Docker Compose, export a secret before starting:

```bash
export AUDIT_SECRET_KEY="$(openssl rand -hex 32)"
docker compose up --build
```

Compose binds `127.0.0.1:8000` by default. Do not expose the legacy API publicly without additional controls.

## Tests and project layout

```bash
python -m pip check
python -m compileall -q agents spine_fracture_stability_agent cli.py spine_stability.py enrichment.py
pytest -q
node tests/browser_ui.test.cjs
```

Key files: `spine_fracture_stability_agent/scoring.py` (reference scoring), `web/index.html` (browser app), `agents/` (legacy supervisor/API), `spine_stability.py` and `spine_fracture_stability_agent/` (older compatibility workflows), and `tests/` (regression tests).

## References

- [Thoracolumbar Injury Classification and Severity Score (TLICS): framework and scoring table](https://pmc.ncbi.nlm.nih.gov/articles/PMC2779435/)
- [Subaxial Injury Classification (SLIC): development and point definitions](https://pmc.ncbi.nlm.nih.gov/articles/PMC3032869/)
- [WFNS Spine Committee recommendations for subaxial cervical spine injuries](https://pmc.ncbi.nlm.nih.gov/articles/PMC7788423/)

## License

MIT — see [LICENSE](LICENSE).
