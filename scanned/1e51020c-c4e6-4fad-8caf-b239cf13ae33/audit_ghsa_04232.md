# [H] OpenClaw: MCP Streamable HTTP redirects could forward configured custom headers to another origin

## Summary
Severity: High
Advisory: GHSA-rjxq-qqhf-8hwh
CVE: CVE-2026-53840
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-rjxq-qqhf-8hwh
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.12

## Details
### Summary

OpenClaw supports remote MCP Streamable HTTP servers with operator-configured custom headers. In affected releases, those headers could be forwarded when the MCP endpoint responded with a cross-origin redirect.

This issue is limited to configured MCP Streamable HTTP servers that use custom headers. It does not expose unrelated OpenClaw credentials.

### Affected configurations

This affects deployments where an MCP server is configured with:

- `transportType: "streamable-http"`
- sensitive custom headers under `mcp.servers.*.headers`
- an MCP endpoint that is malicious, compromised, or able to redirect to another origin

### Impact

Custom MCP headers, such as API keys or tenant-routing headers, could be sent to the redirect target. The exposed credential scope depends on the header the operator configured for that MCP server.

### Patched Versions

The first stable patched version is `2026.5.12`.

### Mitigations

Upgrade to `openclaw@2026.5.8` or later. Before upgrading, avoid custom MCP headers with servers you do not fully trust, and rotate any MCP-specific credentials that may have been exposed by a redirecting endpoint.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rjxq-qqhf-8hwh
- https://nvd.nist.gov/vuln/detail/CVE-2026-53840
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-custom-header-leakage-via-mcp-streamable-http-cross-origin-redirects
