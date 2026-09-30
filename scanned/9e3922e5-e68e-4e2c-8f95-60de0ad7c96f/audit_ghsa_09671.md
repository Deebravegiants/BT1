# [M] n8n-MCP: Sensitive MCP tool-call arguments logged on authenticated requests in HTTP mode

## Summary
Severity: Medium
Advisory: GHSA-wg4g-395p-mqv3
CVE: CVE-2026-42282
CWE: CWE-532
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-25
Source: https://github.com/advisories/GHSA-wg4g-395p-mqv3
Type: github-advisory

## Affected
- npm: `n8n-mcp` — affected >=0 <2.47.13

## Details
### Impact

When `n8n-mcp` runs in HTTP transport mode, authenticated MCP `tools/call` requests had their full arguments and JSON-RPC params written to server logs by the request dispatcher and several sibling code paths before any redaction. When a tool call carries credential material — most notably `n8n_manage_credentials.data` — the raw values can be persisted in logs.

In deployments where logs are collected, forwarded to external systems, or viewable outside the request trust boundary (shared log storage, SIEM pipelines, support/ops access), this can result in disclosure of:

- bearer tokens and OAuth credentials sent through `n8n_manage_credentials`
- per-tenant API keys and webhook auth headers embedded in tool arguments
- arbitrary secret-bearing payloads passed to any MCP tool

The issue requires authentication (`AUTH_TOKEN` accepted by the server), so unauthenticated callers cannot trigger it; the runtime exposure is also reduced by an existing console-silencing layer in HTTP mode, but that layer is fragile and the values are still constructed and passed into the logger. The fix removes the leak at the source.

Impact category: **CWE-532** (Insertion of Sensitive Information into Log File). CVSS 3.1 score: **4.3 Medium** (`AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N`).

### Affected

Deployments running n8n-mcp **v2.47.12 or earlier** in HTTP transport mode (`MCP_MODE=http`). The stdio transport short-circuits the relevant log calls and is not affected in practice.

### Patched

**v2.47.13** and later.

- npm: `npx n8n-mcp@latest` (or pin to `>= 2.47.13`)
- Docker: `docker pull ghcr.io/czlonkowski/n8n-mcp:latest`

The patch routes tool-call arguments through a metadata-only summarizer (`summarizeToolCallArgs`) that records type, top-level key names, and approximate size — never values. The same pattern was adopted earlier for HTTP request bodies in GHSA-pfm2-2mhg-8wpx.

### Workarounds

If developers cannot upgrade immediately:

- Restrict access to the HTTP port (firewall, reverse proxy, or VPN) so only trusted clients can authenticate.
- Restrict access to server logs (no shared SIEM ingestion, no support read-only access) until the upgrade lands.
- Switch to stdio transport (`MCP_MODE=stdio`, the default for CLI invocation), which has no HTTP surface and short-circuits the affected log calls.

### Credit

n8n-MCP thanks [@Mirr2](https://github.com/Mirr2) (Organization / Jormungandr) for reporting this issue.

## References
- https://github.com/czlonkowski/n8n-mcp/security/advisories/GHSA-wg4g-395p-mqv3
- https://nvd.nist.gov/vuln/detail/CVE-2026-42282
- https://github.com/czlonkowski/n8n-mcp/commit/59b665bda36797823df238aeaf20adb862c9f451
- https://github.com/czlonkowski/n8n-mcp
- https://github.com/czlonkowski/n8n-mcp/releases/tag/v2.47.13
