# [M] Coroot 1.20.2 through 1.24.5 Unvalidated Redirect URI in MCP OAuth Client Registration

## Summary
Severity: Medium
Advisory: CVE-2026-79786
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-79786
Type: osv

## Details
Coroot's unauthenticated MCP OAuth dynamic client registration endpoint accepts any syntactically valid redirect URI without validation, allowing attackers to register clients pointing to attacker-controlled hosts. Attackers can send authorization URLs to signed-in users, capture their authorization codes upon consent approval, and exchange them for access tokens to hijack MCP sessions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79786.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-79786
- https://www.vulncheck.com/advisories/coroot-1.20.2-through-1.24.5-unvalidated-redirect-uri-in-mcp-oauth-client-registration
- https://github.com/coroot/coroot/issues/929
- https://github.com/coroot/coroot
- https://github.com/coroot/coroot/blob/v1.24.5/api/mcp_oauth.go
