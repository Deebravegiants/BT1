# [M] n8n-MCP Logs Sensitive Request Data on Unauthorized /mcp Requests

## Summary
Severity: Medium
Advisory: GHSA-pfm2-2mhg-8wpx
CVE: CVE-2026-41495
CWE: CWE-532
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-23
Source: https://github.com/advisories/GHSA-pfm2-2mhg-8wpx
Type: github-advisory

## Affected
- npm: `n8n-mcp` — affected >=0 <2.47.11

## Details
### Impact

When `n8n-mcp` runs in HTTP transport mode, incoming requests to the `POST /mcp` endpoint had their request metadata written to server logs regardless of the authentication outcome. In deployments where logs are collected, forwarded to external systems, or viewable outside the request trust boundary (shared log storage, SIEM pipelines, support/ops access), this can result in disclosure of:

- bearer tokens from the `Authorization` header
- per-tenant API keys from the `x-n8n-key` header in multi-tenant setups
- JSON-RPC request payloads sent to the MCP endpoint

Access control itself was not bypassed — unauthenticated requests were correctly rejected with `401 Unauthorized` — but sensitive values from those rejected requests could still be persisted in logs.

Impact category: **CWE-532** (Insertion of Sensitive Information into Log File).

### Affected

Deployments running n8n-mcp **v2.47.10 or earlier** in HTTP transport mode (`MCP_MODE=http`). The stdio transport is not affected.

### Patched

**v2.47.11** and later.

- npm: `npx n8n-mcp@latest` (or pin to `>= 2.47.11`)
- Docker: `docker pull ghcr.io/czlonkowski/n8n-mcp:latest`

### Workarounds

If users cannot upgrade immediately:

- Restrict network access to the HTTP port (firewall, reverse proxy, or VPN) so only trusted clients can reach the endpoint.
- Switch to stdio transport (`MCP_MODE=stdio`, the default for CLI invocation), which has no HTTP surface.

### Credit

n8n-MCP thanks [@S4nso](https://github.com/S4nso) (Organization / Jormungandr) for reporting this issue.

## References
- https://github.com/czlonkowski/n8n-mcp/security/advisories/GHSA-pfm2-2mhg-8wpx
- https://nvd.nist.gov/vuln/detail/CVE-2026-41495
- https://github.com/czlonkowski/n8n-mcp
- https://github.com/czlonkowski/n8n-mcp/releases/tag/v2.47.11
