# [H] MCP Server Kubernetes: Tool Access Control Bypass via Presentation-Layer Filtering Without Execution-Layer Enforcement

## Summary
Severity: High
Advisory: GHSA-cr22-wjx7-2w6m
CVE: CVE-2026-46519
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-cr22-wjx7-2w6m
Type: github-advisory

## Affected
- npm: `mcp-server-kubernetes` — affected >=0 <3.6.0

## Details
## Summary

`mcp-server-kubernetes` exposes three environment variables (`ALLOW_ONLY_READONLY_TOOLS`, `ALLOW_ONLY_NON_DESTRUCTIVE_TOOLS`, `ALLOWED_TOOLS`) documented as access controls for restricting which Kubernetes operations are available. These controls are enforced at the tool discovery layer (`tools/list`) but not at the execution layer (`tools/call`). Any client that knows a tool name can invoke it directly regardless of the configured restriction mode. The access control was effectively cosmetic.

Fixed in v3.6.0.

## Impact

An attacker or misconfigured AI agent with network access to the MCP server's HTTP endpoint could invoke any Kubernetes tool regardless of the restriction mode configured by the operator -- including `kubectl_delete`, `exec_in_pod`, `kubectl_generic`, and `node_management`.

The project explicitly supports and documents multi-client HTTP deployment scenarios (Streamable HTTP and SSE transports, in-cluster deployments, Codex CLI and Gemini CLI integrations). In these deployments, operators relied on the tool restriction env vars to enforce least-privilege access across users or roles. The bypass invalidated that model entirely.

Severity scales with the Kubernetes service account's permissions. In environments where the MCP server runs with `cluster-admin` (common in dev/staging), this is equivalent to full cluster compromise for any client that can reach the endpoint.

The `MCP_AUTH_TOKEN` / `X-MCP-AUTH` mechanism controls who can reach the endpoint but provides no per-tool authorization. An authenticated client restricted to `ALLOWED_TOOLS=kubectl_get` could still invoke `kubectl_delete` after authentication.

## Root Cause

In `src/index.ts`, the `ListToolsRequestSchema` handler applied the configured filtering logic before returning available tools. The `CallToolRequestSchema` handler dispatched directly by tool name with no equivalent check -- every tool was reachable unconditionally.

## Proof of Concept

Tested across all three restriction modes against a live kind cluster. In each case, `kubectl_delete` was absent from `tools/list` but executed successfully via a direct `tools/call` request:

```shell
curl -s http://<HOST>:3003/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"kubectl_delete","arguments":{"resourceType":"pod","name":"test-pod","namespace":"default"}}}'
```

Result: `{"result":{"content":[{"type":"text","text":"pod \"test-pod\" deleted\n"}]}}`

Confirmed across `ALLOW_ONLY_READONLY_TOOLS=true`, `ALLOW_ONLY_NON_DESTRUCTIVE_TOOLS=true`, and `ALLOWED_TOOLS=kubectl_get`.

## Remediation

The fix applies the same filtering logic from `ListToolsRequestSchema` at the start of the `CallToolRequestSchema` handler, returning an error for any tool call outside the active allowed set. Fixed in v3.6.0.

## Credit

Discovered by [Francisco Rosales](https://www.linkedin.com/in/francisco-rosales-celis/) of [Manifold Security](https://manifold.security), coordinated by [Ax Sharma](https://www.linkedin.com/in/axsharma/), Head of Research at Manifold Security.

## References
- https://github.com/Flux159/mcp-server-kubernetes/security/advisories/GHSA-cr22-wjx7-2w6m
- https://nvd.nist.gov/vuln/detail/CVE-2026-46519
- https://github.com/Flux159/mcp-server-kubernetes
- https://github.com/Flux159/mcp-server-kubernetes/releases/tag/v3.6.0
