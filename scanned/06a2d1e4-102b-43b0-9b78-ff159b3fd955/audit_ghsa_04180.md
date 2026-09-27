# [H] Kozou: Unauthenticated MCP HTTP server and bundled dev-stack hardening (DNS-rebinding, request-body limits, read-only reads, default network exposure)

## Summary
Severity: High
Advisory: GHSA-v52w-28xh-v562
CWE: CWE-1188, CWE-272, CWE-346, CWE-770
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-v52w-28xh-v562
Type: github-advisory

## Affected
- npm: `kozou` — affected >=0 <1.8.1
- npm: `@kozou/api` — affected >=0 <1.8.1
- npm: `@kozou/mcp` — affected >=0 <1.8.1
- npm: `@kozou/core` — affected >=0 <1.8.1

## Details
Kozou compiles a PostgreSQL schema into an Admin UI, a REST API, and an MCP server. Several hardening gaps in the bundled HTTP surfaces and the scaffolded dev stack are fixed in **1.8.1**.

## Issues

1. **MCP HTTP server lacked DNS-rebinding protection.** The Streamable HTTP transport is unauthenticated and loopback by default. Without `Host`/`Origin` validation, a malicious web page in the operator's browser could rebind a hostname it controls to the loopback address and drive the MCP endpoint — reading schema metadata, or (when the opt-in `call` execution tool is enabled) executing exposed functions as the execution role.

2. **Unbounded request-body buffering (DoS).** Both the MCP HTTP server and the in-house REST server read the entire request body into memory with no size limit, so a reachable client could drive the process toward memory exhaustion.

3. **Read requests ran in a read/write transaction.** The shared role-transaction envelope opened every request with a plain `BEGIN`, so a `GET` ran read/write. A `SELECT` that reaches a volatile function or a writable / `INSTEAD`-triggered view could perform a write that then commits — the "a GET only reads" contract was left to the serving role's grants rather than enforced.

4. **No-auth dev surfaces published on all interfaces by default.** The scaffolded `docker-compose.yml` (and the quickstart) published the unauthenticated Admin UI and MCP HTTP server — and the default-credential demo database — on every host interface, and the config defaulted those binds to `0.0.0.0`.

## What changed in 1.8.1

- **DNS-rebinding guard (MCP HTTP):** the server validates the `Host` header (and a present `Origin`) against an allowlist before handling any request, on every route. Matching is on the hostname; loopback names are always accepted and an operator can add hosts via configuration. A browser cannot forge `Host`/`Origin`, so this closes the rebinding vector. (This is a browser-rebinding defence; network reachability of an unauthenticated server must still be constrained by the network — see workarounds.)
- **Request-body size cap:** both HTTP servers reject an over-large declared `Content-Length` (413) and enforce the limit while streaming, so a chunked / `Content-Length`-less body cannot grow unbounded. A non-JSON `Content-Type` on a body is rejected with 415. The cap is configurable.
- **Read-only read transactions:** read methods (`GET`) now run in a `READ ONLY` transaction, so the database refuses any write for the duration of the request regardless of the role's grants.
- **Loopback-by-default network posture:** the Admin UI and MCP HTTP server now bind loopback by default; the bundled compose files publish every host port (Admin UI, MCP, database) on `127.0.0.1` only, while the container binds all interfaces internally so the loopback mapping still works. Operators opt into a broader bind explicitly.

## Impact

The MCP HTTP server's exposure is greatest when the opt-in `call` execution tool is enabled and/or the server is reachable beyond loopback. The read/write-transaction issue has effect only when the schema exposes a read path that can write (a volatile-function-backed column or a writable/`INSTEAD`-triggered view) and the serving role holds write grants. The all-interface publish affected anyone who ran the scaffolded `docker compose up` on a host reachable from an untrusted network. Requests run under `SET LOCAL ROLE`, so PostgreSQL still enforces grants/RLS at runtime; these are defense-in-depth and read-contract hardening.

## Affected / patched

- npm packages `kozou`, `@kozou/api`, `@kozou/mcp`, `@kozou/core` (and the lockstep-versioned siblings): affected `<= 1.8.0`, patched **1.8.1**.
- Container image `ghcr.io/kozou-dev/kozou`: patched at tag `v1.8.1`.

## Workarounds (if you cannot upgrade immediately)

- Bind the Admin UI and MCP HTTP server to loopback and publish their host ports on `127.0.0.1` only; do not expose them to untrusted networks.
- Do not enable the MCP `call` execution tool on a non-loopback / unauthenticated deployment.
- Put an authenticating reverse proxy (with `Host`/`Origin` validation and a request-body limit) in front of any non-loopback deployment.
- Change the demo database's default credentials and restrict its port.

## Patches

Upgrade to **Kozou 1.8.1** (all npm packages and the `ghcr.io/kozou-dev/kozou` image).

## References
- https://github.com/kozou-dev/kozou/security/advisories/GHSA-v52w-28xh-v562
- https://github.com/kozou-dev/kozou
