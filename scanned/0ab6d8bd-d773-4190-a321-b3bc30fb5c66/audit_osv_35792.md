# [H] Authentication Bypass and Audience Confusion in MCP Toolbox OAuth Provider

## Summary
Severity: High
Advisory: CVE-2026-14541
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/CVE-2026-14541
Type: osv

## Details
An authentication bypass and audience confusion vulnerability exists in the Google OAuth provider component of Google mcp-toolbox version 1.4.0. When a Google authService is initialized with mcpEnabled: true but lacks an explicitly defined audience or clientId, the ValidateMCPAuth pipeline for opaque tokens skips audience validation entirely. As a result, the toolbox will accept any valid Google OAuth access token—even those minted for unrelated ecosystem applications—granting unauthorized clients access to protected tools and data backends.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14541.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-14541
- https://github.com/googleapis/mcp-toolbox/pull/3450
