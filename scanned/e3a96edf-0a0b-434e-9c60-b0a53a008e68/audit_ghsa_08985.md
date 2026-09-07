# [C] MCP Gateway: Authority-injection and JWT/session bypass via the unauthenticated router hair-pin "router-key" / "mcp-init-host" path

## Summary
Severity: Critical
Advisory: GHSA-g53w-w6mj-hrpp
CWE: CWE-287, CWE-346, CWE-639
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-g53w-w6mj-hrpp
Type: github-advisory

## Affected
- Go: `github.com/Kuadrant/mcp-gateway` — affected >=0 <0.7.0

## Details
## Summary
 
The MCP router (ext_proc) exposes an `initialize`-method code path that, when a
request carries an `mcp-init-host` header, bypasses the gateway JWT session
validator and rewrites the upstream `:authority` header to whatever the caller
chooses, gated only by a single shared header value (`router-key`). The shared
value is

* a literal string (`secret-api-key`) baked into `cmd/mcp-broker-router/main.go`
  as a fall-back default, and
* in controller-managed deployments, a SHA-256 truncation of the
  `MCPGatewayExtension` UID — a non-secret value visible to anyone with `get`
  permission on the resource, and additionally exposed in `argv` because it is
  passed to the broker-router container via `--mcp-router-key=...`.

A request that satisfies the trivial header check is forwarded to any backend
listener registered with the gateway (including external services such as
`api.githubcopilot.com` when configured), bypassing both the broker (where the
signed `x-mcp-authorized` capability filter is enforced) and the gateway's
JWT-based session model.

## References
- https://github.com/Kuadrant/mcp-gateway/security/advisories/GHSA-g53w-w6mj-hrpp
- https://github.com/Kuadrant/mcp-gateway/commit/6052079283472aff99727058c92618178f86b2d7
- https://github.com/Kuadrant/mcp-gateway
- https://github.com/Kuadrant/mcp-gateway/releases/tag/v0.7.0
