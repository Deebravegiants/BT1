# [C] PraisonAI: AgentOS remains unauthenticated after incomplete fix version and allows remote agent invocation

## Summary
Severity: Critical
Advisory: GHSA-892r-p3jq-jp24
CVE: CVE-2026-57116
CWE: CWE-200, CWE-306, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-892r-p3jq-jp24
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=4.2.1 <4.6.59

## Details
# AgentOS remains unauthenticated after GHSA-pm96 patched version and allows remote agent invocation

## Summary

PraisonAI's `AgentOS` FastAPI deployment surface remains unauthenticated in
current main and in releases after the published patched version for
`GHSA-pm96-6xpr-978x` / `CVE-2026-40151`.

The public AgentOS advisory is published as an instruction-disclosure issue
with affected versions `< 4.5.128` and patched version `4.5.128`. However,
`v4.5.128`, latest release `v4.6.57`, and current main still register
`GET /api/agents` and `POST /api/chat` without authentication. The chat route
directly calls `agent.chat(request.message)`. No-auth and wrong-bearer requests
both execute the deployed agent.

This is broader than passive metadata disclosure. In any deployment where
AgentOS wraps agents with tools, private context, memory, API integrations, or
cost-bearing model calls, an unauthenticated reachable client can drive those
agents.

## Affected Product

- Repository: `MervinPraison/PraisonAI`
- Package: `praisonai`
- Component: `src/praisonai/praisonai/app/agentos.py`
- Config component: `src/praisonai-agents/praisonaiagents/app/config.py`
- Public advisory incomplete-fix reference: `GHSA-pm96-6xpr-978x` /
  `CVE-2026-40151`

Confirmed affected dynamically:

- `v4.5.126`
- `v4.5.128` (published patched version for `GHSA-pm96-6xpr-978x`)
- `v4.6.9`
- `v4.6.10`
- `v4.6.56`
- `v4.6.57`
- current main `2f9677abb2ea68eab864ee8b6a828fd0141612e1`

Static source review found the same unauthenticated route pattern and
`0.0.0.0` default in `v4.2.1`.

Suggested affected range: `>= 4.2.1, <= 4.6.57`.

## Root Cause

`AgentOSConfig` / `AgentAppConfig` defaults the deployment host to all
interfaces and has no authentication fields:

```python
name: str = "PraisonAI App"
host: str = "0.0.0.0"
port: int = 8000
api_prefix: str = "/api"
```

`AgentOS._register_routes()` registers public agent metadata and chat routes
without middleware, dependency, API key check, bearer-token check, or startup
fail-closed guard:

```python
@app.get(f"{self.config.api_prefix}/agents")
async def list_agents():
    return {"agents": [...]}

@app.post(f"{self.config.api_prefix}/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    ...
    response = agent.chat(request.message)
```

A wrong `Authorization` header is ignored because the route does not inspect it.

Current main also has a root-export bug where `from praisonai import AgentOS`
raises `ImportError`, but this does not mitigate the issue. The same class
remains reachable through `from praisonai import AgentApp` and
`from praisonai.app import AgentOS`.

## Why This Is Not Intended Behavior

PraisonAI's security documentation says API servers were hardened so anonymous
requests return `401` and default binding changed from `0.0.0.0` to
`127.0.0.1` after the prior unauthenticated API server class.

The API Server Authentication docs say bearer auth is enabled by default,
disabling auth is not recommended for production, and `0.0.0.0` should be used
only behind an authenticating proxy.

The local PoV includes a hardened sibling control for the generated deploy API
on current main. It returns:

- no auth: `401`
- wrong bearer: `401`
- correct bearer: `200`

AgentOS remains outside that control plane and still accepts no-auth and
wrong-bearer `/api/chat` requests.

## Local PoV

The PoV is local-only. It uses FastAPI's in-process test client, a stub agent,
and a temporary file side effect. It does not start a network listener, call an
LLM provider, or contact any external service.

Command:

```bash
env PYTHONPATH="artifacts/repos/praisonai-current/src/praisonai:artifacts/repos/praisonai-current/src/praisonai-agents" \
  uv run --with fastapi --with httpx --with flask --with flask-cors \
    --with pydantic --with typing-extensions --with rich --with python-dotenv \
    submission-bundle/praisonai-prai-cand-007-agentos-incomplete-auth-fix/poc/prai_cand_007_agentos_incomplete_auth_fix.py \
    --repo artifacts/repos/praisonai-current \
    --label current-head
```

Current-head result summary:

```json
{
  "describe": "v4.6.57-4-g2f9677ab",
  "head": "2f9677abb2ea68eab864ee8b6a828fd0141612e1",
  "agentos_vulnerable": true,
  "entrypoints": [
    {
      "entrypoint": "agentapp_alias",
      "statuses": [200, 200, 200],
      "side_effects": ["no-auth-marker", "wrong-bearer-marker"]
    },
    {
      "entrypoint": "direct_agentos",
      "statuses": [200, 200, 200],
      "side_effects": ["no-auth-marker", "wrong-bearer-marker"]
    }
  ],
  "deploy_api_control": {
    "control_passed": true,
    "statuses": [401, 401, 200]
  }
}
```

The three AgentOS statuses are for:

- unauthenticated `GET /api/agents`;
- unauthenticated `POST /api/chat`;
- wrong-bearer `POST /api/chat`.

The side-effect list proves both unauthenticated chat requests invoked the
agent method.

Minimal inline reproducer:

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient
from praisonai import AgentApp
from praisonaiagents import AgentOSConfig

class StubAgent:
    name = "pov_agentos_agent"
    role = "tester"
    instructions = "private instruction marker"

    def __init__(self, out):
        self.out = out

    def chat(self, message):
        self.out.write_text(self.out.read_text() + message + "\n")
        return "PRAI_CAND_007_AGENTOS_EXECUTED:" + message

with TemporaryDirectory() as tmp:
    side_effect = Path(tmp) / "side_effects.txt"
    side_effect.write_text("")
    app = AgentApp(
        agents=[StubAgent(side_effect)],
        config=AgentOSConfig(host="0.0.0.0", port=8000),
    )
    client = TestClient(app.get_app())

    assert client.get("/api/agents").status_code == 200
    assert client.post("/api/chat", json={"message": "no-auth"}).status_code == 200
    assert client.post(
        "/api/chat",
        headers={"Authorization": "Bearer definitely-wrong"},
        json={"message": "wrong-bearer"},
    ).status_code == 200
    assert side_effect.read_text().splitlines() == ["no-auth", "wrong-bearer"]
```

## Version Sweep

| Target | Result |
| --- | --- |
| `v4.5.126` | vulnerable |
| `v4.5.128` | vulnerable |
| `v4.6.9` | vulnerable |
| `v4.6.10` | vulnerable |
| `v4.6.56` | vulnerable; generated deploy API control returns `401/401/200` |
| `v4.6.57` | vulnerable; generated deploy API control returns `401/401/200` |
| current `2f9677abb` | vulnerable; generated deploy API control returns `401/401/200` |

Evidence files are retained locally under the bundle's `evidence/` directory
and can be provided if useful.

## Duplicate / Incomplete-Fix Notes

This report is related to `GHSA-pm96-6xpr-978x` / `CVE-2026-40151`. The
published advisory describes AgentOS instruction disclosure and lists
`4.5.128` as patched. It also mentions unauthenticated `/api/chat` as a chained
instruction-extraction path.

The current report should be treated as an incomplete fix / affected-range
correction with a broader demonstrated impact:

- the published patched version `v4.5.128` still reproduces;
- latest release `v4.6.57` still reproduces;
- current main still reproduces;
- the PoV proves unauthorized agent invocation and side effects, not only
  instruction disclosure.

This is distinct from private `PRAI-CAND-003` / `GHSA-x8cv-xmq7-p8xp`, which
covers `praisonaiagents.AgentTeam.launch()` routes. This report covers
`praisonai.app.AgentOS` and `AgentApp` alias routes.

## Impact

If an operator exposes an AgentOS app on a reachable interface, any client that
can reach it can:

- enumerate deployed agents through `GET /api/agents`;
- read agent names, roles, and instruction snippets;
- invoke the default agent or a named agent through `POST /api/chat`;
- trigger downstream tools, private context reads, memory accesses, API
  integrations, browser actions, or other side effects attached to the agent;
- consume model/API budget through repeated invocation.

The exact downstream impact depends on the deployed agents. The framework-level
boundary failure is that a production deployment surface exposes agent control
without authentication and defaults to binding on all interfaces.

## Suggested Fix

Use the same security model already applied to generated API deployments:

- add authentication fields to `AgentOSConfig` / `AgentAppConfig`;
- default auth to enabled;
- default bind host to `127.0.0.1`;
- reject no-auth and wrong-bearer requests for `GET /api/agents` and
  `POST /api/chat`;
- fail closed for non-loopback binds unless auth is configured or an explicit
  unsafe development opt-out is set;
- avoid returning instruction text from unauthenticated metadata endpoints;
- add regression tests for no auth, wrong bearer, correct bearer, and external
  bind without auth.

Maintainers can either update `GHSA-pm96-6xpr-978x` with the corrected affected
range and broader impact or publish a separate incomplete-fix advisory.

## Suggested Severity

Suggested severity: Critical.

The Critical score matches the unauthenticated agent-control model: network
attacker, low complexity, no privileges, no user interaction, and high
deployment-dependent impact when agents are connected to tools, private data,
or cost-bearing services. If maintainers score only a minimal no-tool demo
agent, the impact may be lower, but the current default framework behavior is
still unauthenticated agent invocation.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-892r-p3jq-jp24
- https://github.com/MervinPraison/PraisonAI
