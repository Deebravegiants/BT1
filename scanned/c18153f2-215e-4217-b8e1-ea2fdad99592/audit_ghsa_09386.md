# [H] n8n-mcp affected by path traversal, redirect-following SSRF, and telemetry payload exposure

## Summary
Severity: High
Advisory: GHSA-8g7g-hmwm-6rv2
CWE: CWE-200, CWE-22, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-8g7g-hmwm-6rv2
Type: github-advisory

## Affected
- npm: `n8n-mcp` — affected >=0 <2.50.1

## Details
## Impact

`n8n-mcp` versions before 2.50.1 contained three independently-reported issues affecting deployments that run the n8n API integration:

1. **Caller-supplied identifiers were not validated before being used as URL path segments** by the n8n API client. An authenticated MCP caller passing a crafted workflow id could cause outbound requests carrying the configured n8n API key to land on other same-origin endpoints, bypassing handler-level access controls (including `DISABLED_TOOLS`).

2. **Validated webhook, form, and chat trigger URLs followed redirects.** A URL that passed initial validation could redirect the outbound request to a host that would otherwise have been rejected, with the response body returned to the caller. Reachable as non-blind SSRF over authenticated MCP calls.

3. **Mutation telemetry stored unredacted operation payloads.** On instances running with the default opt-in telemetry, partial-update operation diffs were uploaded without redaction. Operation values can carry the same node-parameter values the workflow contains, including bearer tokens, API keys, and webhook secrets.

## Severity

CVSS 8.3 (HIGH). Exploitation requires an authenticated MCP caller and an n8n API integration configured with an n8n API key.

## Patched versions

Upgrade to `n8n-mcp >= 2.50.1`.

## Workarounds

- For issues (1) and (2): restrict network access to the HTTP transport (firewall, reverse-proxy ACL, or VPN) so only trusted callers can reach the MCP HTTP port; or switch to stdio mode, which exposes no HTTP surface for these issues.
- For issue (3): set `N8N_MCP_TELEMETRY_DISABLED=true` in the environment before starting the server, or run `npx n8n-mcp telemetry disable` once.

## Credit

Reported by @cybercraftsolutionsllc.

## References
- https://github.com/czlonkowski/n8n-mcp/security/advisories/GHSA-8g7g-hmwm-6rv2
- https://github.com/czlonkowski/n8n-mcp/commit/1cfe9c6bddb4b1634e6e23323c18ea35fd196999
- https://github.com/czlonkowski/n8n-mcp
- https://github.com/czlonkowski/n8n-mcp/releases/tag/v2.50.1
