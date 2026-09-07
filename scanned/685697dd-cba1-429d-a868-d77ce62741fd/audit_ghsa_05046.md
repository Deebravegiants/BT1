# [C] npm PraisonAI AgentOS exposes unauthenticated agent listing and invocation

## Summary
Severity: Critical
Advisory: GHSA-9752-mhqh-h34f
CVE: CVE-2026-57140
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-9752-mhqh-h34f
Type: github-advisory

## Affected
- npm: `praisonai` — affected >=1.6.0 <1.7.2

## Details
## Summary

The published npm package `praisonai` ships a TypeScript `AgentOS` HTTP server that defaults to `host: "0.0.0.0"` and registers sensitive agent routes without any authentication or authorization middleware.

When a developer starts `AgentOS`, a network attacker who can reach the service can:

- read configured agent names, roles, and the first 100 characters of each agent's instructions through `GET /api/agents`; and
- invoke the selected agent through `POST /api/chat` without credentials.

This is distinct from the existing Python/PyPI AgentOS and API-server advisories. The affected package here is `npm:praisonai`; the current published npm package is `1.7.1`, and the same TypeScript source is still present in refreshed `origin/main` at `v4.6.58`.

## Technical Details

`AgentOSConfig` exposes host, CORS, and API-prefix settings but no authentication token, auth mode, or authorization callback.

Relevant current-head source:

```text
src/praisonai-ts/src/os/config.ts
  26: host?: string;              // default: "0.0.0.0"
  35: corsOrigins?: string[];     // default: ["*"]
  66: export const DEFAULT_AGENTOS_CONFIG = {
  68:     host: '0.0.0.0',
  71:     corsOrigins: ['*'],
```

`AgentOS._createApp()` registers JSON parsing and CORS handling, then immediately registers routes. There is no middleware between body parsing and route registration that validates an API key, bearer token, session, origin-bound secret, or any other credential.

Relevant current-head source:

```text
src/praisonai-ts/src/os/agentos.ts
  179: app.use(express.json());
  182: // Add CORS middleware
  204: // Register routes
  205: this._registerRoutes(app);
```

The sensitive routes are then exposed:

```text
src/praisonai-ts/src/os/agentos.ts
  235: app.get(`${apiPrefix}/agents`, ...)
  240: instructions: agent.instructions ? ... : null
  250: app.post(`${apiPrefix}/chat`, ...)
  273: const response = await agent.chat(message);
  331: const host = options.host || this.config.host;
  338: this._server = app.listen(port, host, ...)
```

Because the default host is `0.0.0.0`, `await app.serve({ port: 8000 })` listens on all interfaces unless the developer explicitly overrides `host`.

### Why This Is Not Intended Behavior

PraisonAI's official TypeScript documentation describes the npm package as a production-ready multi-agent framework and directs users to install it with `npm install praisonai`.

PraisonAI's security documentation says security reports should include affected versions, impact, reproduction steps, and a suggested fix, and states that GitHub Security Advisories are the preferred reporting method. The same security page also documents a prior hardening change where API servers were changed to require authentication by default and bind to `127.0.0.1` instead of `0.0.0.0`.

The TypeScript npm `AgentOS` implementation still does the opposite:

- default bind address is `0.0.0.0`;
- no auth config exists in `AgentOSConfig`;
- `/api/agents` discloses agent metadata and instruction prefixes; and
- `/api/chat` invokes `agent.chat(message)` directly.

The patched-control branch in the PoV confirms that adding a pre-route bearer-token middleware makes the same unauthenticated requests fail with `401`.

## PoV

The PoV installs the published npm package in a temporary project, starts `AgentOS` on `127.0.0.1` with a mock agent, and sends loopback HTTP requests. It does not call any LLM provider or external service after package installation.

Run from a local reproduction checkout:

```fish
node poc/pov_poc.js 1.7.1
```

Observed result:

```json
{
  "version": "1.7.1",
  "defaultHost": "0.0.0.0",
  "agentsStatus": 200,
  "agentsBody": {
    "agents": [
      {
        "name": "finance-admin",
        "role": "internal finance operations",
        "instructions": "poc SECRET: refund-wire-tool may alter customer balances"
      }
    ]
  },
  "chatStatus": 200,
  "chatBody": {
    "response": "agent-invoked:transfer-check",
    "agent_name": "finance-admin"
  },
  "invokedMessages": [
    "transfer-check"
  ]
}
```

No `Authorization` header is sent in the vulnerable requests.

The PoV also applies a minimal local-only auth middleware patch to the temporary installed copy and reruns the same requests as a control:

```json
{
  "patchedNoAuthAgents": 401,
  "patchedNoAuthChat": 401,
  "patchedWithAuthAgents": 200,
  "patchedWithAuthChat": 200
}
```

This control demonstrates that the PoV is exercising the missing authentication boundary, not an artifact of the mock agent.

## PoC

The PoV section above contains the local reproduction command, input, and decisive output.

## Impact

An attacker who can reach a running TypeScript `AgentOS` server can invoke configured agents without credentials. Real impact depends on the deployed agent, but PraisonAI agents may have access to tools, memory, workflow state, external APIs, credentials in process environment, and business data. Unauthorized prompt injection through `/api/chat` can therefore affect confidentiality and integrity of downstream systems reachable by the configured agent.

`GET /api/agents` also discloses agent names, roles, and instruction prefixes, which can reveal internal workflow details and help tailor prompts against the exposed agent.

This report does not claim arbitrary code execution by default. If the deployed agent has code, file, browser, MCP, or business-operation tools, the unauthenticated invocation endpoint can become the entry point for those tool-side effects.

### Severity

Suggested severity: Critical.

Rationale:

- `AV`: the vulnerable component is an HTTP service and defaults to all-interface binding.
- `AC`: exploitation is a direct HTTP request.
- `PR`: no credentials are required.
- `UI`: no user interaction is required after the server is running.
- `S`: impact is within the vulnerable service and the configured agent's authority.
- `C`: `/api/agents` exposes instructions and `/api/chat` can elicit data reachable by the agent.
- `I`: `/api/chat` lets unauthenticated callers drive agent/tool actions.
- `A`: unauthorized callers can consume model/API/server resources.

## Suggested Fix

Recommended minimum fix:

1. Add an authentication configuration to TypeScript `AgentOSConfig`, for example `authToken`, `authRequired`, or an `authorize(req)` callback.
2. Default externally reachable servers to authenticated. Prefer fail-closed behavior when `host` is not loopback.
3. Change the default host from `0.0.0.0` to `127.0.0.1`, matching the documented Python API-server hardening.
4. Register auth middleware before all non-health routes, including `/`, `/api/agents`, `/api/chat`, `/api/teams`, and `/api/flows`.
5. Avoid returning agent instruction text from `/api/agents` unless the caller is authenticated and explicitly authorized.
6. Add regression tests that:
   - unauthenticated `GET /api/agents` returns `401`;
   - unauthenticated `POST /api/chat` returns `401` and does not call `agent.chat`;
   - authenticated requests still work;
   - default `serve({ port })` binds to loopback or fails closed when auth is not configured.

## Affected Package/Versions

- Repository: `MervinPraison/PraisonAI`
- Ecosystem: `npm`
- Package: `praisonai`
- Current npm version: `1.7.1`
- Component: `src/praisonai-ts/src/os/agentos.ts`
- Config component: `src/praisonai-ts/src/os/config.ts`
- Refreshed repo head checked: `1ad58ca02975ff1398efeda694ea2ab78f20cf3e` (`v4.6.58`)

Confirmed affected npm versions:

```text
>= 1.6.0, <= 1.7.1
```

Boundary:

```text
<= 1.5.4 did not ship dist/os/agentos.js in the npm tarball.
```

No fixed npm version is known at the time of this report.

### Version Sweep

The included sweep downloads npm tarballs and checks for the shipped `dist/os` implementation:

```fish
node poc/version_sweep_poc.js
```

Affected rows:

```text
version  has_agentos  default_host_0_0_0_0  has_api_agents_instructions  has_api_chat_agent_invocation  has_401_unauthorized_guard  mentions_authorization_header
1.6.0    true         true                  true                         true                           false                       true
1.7.0    true         true                  true                         true                           false                       true
1.7.1    true         true                  true                         true                           false                       true
```

Earlier npm versions through `1.5.4` did not ship `dist/os/agentos.js`.

`mentions_authorization_header` is true because CORS allows the `Authorization` header. The sweep separately verifies there is no 401/Unauthorized route guard.

## Advisory History

Checked:

- public GitHub advisories for `MervinPraison/PraisonAI`;
- private/triage advisories visible to this account; and
- visible PraisonAI advisories and prior reports.

No public or private advisory row in that data targets `ecosystem: npm` / `package: praisonai`.

Closest related advisories are Python/PyPI-scoped and do not cover the npm TypeScript package:

- `GHSA-pm96-6xpr-978x`: PyPI `praisonai`, unauthenticated information disclosure via Python AgentOS `/api/agents`, affected `<= 4.5.120`.
- `GHSA-892r-p3jq-jp24`: PyPI `praisonai`, Python AgentOS unauthenticated remote agent invocation, affected `>= 4.2.1, <= 4.6.57`.
- `GHSA-6rmh-7xcm-cpxj`: PyPI `praisonai`, generated legacy API server authentication disabled by default, affected `>= 2.5.6, <= 4.6.33`.
- `GHSA-r7v3-x45f-g7hp` / `GHSA-7ww9-85pg-cv4x`: PyPI `praisonai serve agents --api-key` ignored.

This report should be tracked separately because it affects the npm package and the TypeScript implementation under `src/praisonai-ts`, with npm affected range `>= 1.6.0, <= 1.7.1`.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-9752-mhqh-h34f
- https://github.com/MervinPraison/PraisonAI
