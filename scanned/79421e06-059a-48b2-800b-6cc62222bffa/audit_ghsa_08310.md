# [H] rmcp Streamable HTTP server transport has a DNS rebinding vulnerability

## Summary
Severity: High
Advisory: GHSA-89vp-x53w-74fx
CVE: CVE-2026-42559
CWE: CWE-346, CWE-350
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-89vp-x53w-74fx
Type: github-advisory

## Affected
- crates.io: `rmcp` — affected >=0 <1.4.0

## Details
## Summary

Prior to version 1.4.0, the `rmcp` crate's Streamable HTTP server transport (`crates/rmcp/src/transport/streamable_http_server/`) did not validate the incoming `Host` header. This allowed a malicious public website, via a DNS rebinding attack, to send authenticated requests to an MCP server running on the victim's loopback or private-network interface — violating the MCP specification's [transport security guidance](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#security-warning).

## Impact

An attacker who convinces a victim to visit a malicious page can:

- Enumerate and invoke any tool exposed by a locally-running rmcp-based MCP server.
- Read resources, prompts, and any state accessible via the MCP session.
- Trigger side effects (file writes, shell execution, API calls, etc.) limited only by what tools the victim's server exposes.

Because MCP servers frequently run with the user's privileges and expose developer tooling (filesystems, shells, browser control, language servers, etc.), the practical impact can extend to arbitrary code execution on the victim's machine.

## Affected Versions

`rmcp < 1.4.0` — all prior releases of the Streamable HTTP server transport. Non-HTTP transports (stdio, child-process) are not affected.

## Patched Versions

`rmcp >= 1.4.0` (current: 1.5.1).

## Patch

Fixed in [PR #764](https://github.com/modelcontextprotocol/rust-sdk/pull/764) (commit `8e22aa2`), released as v1.4.0 on 2026-04-09:

- `StreamableHttpServerConfig::allowed_hosts` now defaults to a loopback-only allowlist: `["localhost", "127.0.0.1", "::1"]`.
- All incoming HTTP requests pass through `validate_dns_rebinding_headers()`, which parses the `Host` header and returns HTTP 403 if the host is not on the allowlist.
- Public deployments can configure an explicit allowlist via `StreamableHttpService::with_allowed_hosts(...)`, or opt out (not recommended without an upstream reverse proxy that validates `Host`) via `disable_allowed_hosts()`.

This fix validates the `Host` header only. `Origin` header validation is tracked as a defense-in-depth follow-up in [#822](https://github.com/modelcontextprotocol/rust-sdk/issues/822) and is not required to block the DNS rebinding attack described here — the browser cannot forge the Host header sent to the rebound server.

## Workarounds for Unpatched Users

- Upgrade to `rmcp >= 1.4.0`.
- If upgrade is not possible, place the MCP server behind a reverse proxy (e.g. nginx, Caddy) configured to reject requests whose `Host` header is not one of your expected hostnames.
- Do not bind the MCP server to `0.0.0.0` without such a proxy.

## Resources

- PR: https://github.com/modelcontextprotocol/rust-sdk/pull/764
- Issue: https://github.com/modelcontextprotocol/rust-sdk/issues/815
- Follow-up (Origin validation): https://github.com/modelcontextprotocol/rust-sdk/issues/822
- MCP transport security guidance: https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#security-warning

## Related advisories (same class of vulnerability)

- TypeScript SDK: GHSA-w48q-cv73-mx4w
- Python SDK: GHSA-9h52-p55h-vw2f
- Go SDK: GHSA-xw59-hvm2-8pj6
- Java SDK: GHSA-8jxr-pr72-r468

## References
- https://github.com/modelcontextprotocol/rust-sdk/security/advisories/GHSA-89vp-x53w-74fx
- https://github.com/nubo-db/dynoxide/security/advisories/GHSA-fvh2-gm75-j4j7
- https://nvd.nist.gov/vuln/detail/CVE-2026-42559
- https://github.com/modelcontextprotocol/rust-sdk/issues/815
- https://github.com/modelcontextprotocol/rust-sdk/issues/822
- https://github.com/modelcontextprotocol/rust-sdk/pull/764
- https://github.com/modelcontextprotocol/rust-sdk/commit/8e22aa2de28df5a285eed87c11cd89bf15fa90d3
- https://github.com/modelcontextprotocol/rust-sdk
- https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#security-warning
- https://rustsec.org/advisories/RUSTSEC-2026-0140.html
