# [H] Uni-CLI: Legacy HTTP MCP transport accepted browser-originated localhost requests

## Summary
Severity: High
Advisory: GHSA-v3f4-w7r7-v3hm
CWE: CWE-346, CWE-352
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-v3f4-w7r7-v3hm
Type: github-advisory

## Affected
- npm: `@zenalexa/unicli` — affected >=0 <0.225.2

## Details
## Impact

Uni-CLI versions before 0.225.2 exposed the legacy JSON-RPC-over-HTTP MCP transport on loopback without validating browser Origin headers before routing requests. A malicious web page could send a CORS simple POST request, such as text/plain, to the local /mcp endpoint and deliver a JSON-RPC body to the dispatcher. If the user had started the local MCP HTTP transport, that page could drive tools/call requests against the user's local Uni-CLI server.

The Streamable HTTP transport already enforced this browser-to-localhost boundary. The legacy stateless HTTP path did not, so the two HTTP transports had drifted. This issue is about the browser-to-localhost boundary; it does not change Uni-CLI's local-code-execution trust model.

## Patches

Version 0.225.2 fixes the issue by moving the Origin policy into a shared guard and applying it before routing in both HTTP transports. Non-loopback browser Origins are rejected with HTTP 403 before health, OAuth, or /mcp dispatch runs. Non-browser clients that omit Origin remain supported.

## Workarounds

Upgrade to 0.225.2 or later. If upgrading is not immediately possible, do not expose the legacy HTTP MCP transport to browser-originated traffic; use the default stdio transport or the Streamable HTTP transport instead.

## Credits

Reported privately by Ryan Vonbrubeck ([@dodge1218](https://github.com/dodge1218)).

## References
- https://github.com/olo-dot-io/Uni-CLI/security/advisories/GHSA-v3f4-w7r7-v3hm
- https://github.com/olo-dot-io/Uni-CLI
