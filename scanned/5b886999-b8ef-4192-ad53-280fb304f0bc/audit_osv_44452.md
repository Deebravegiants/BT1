# [C] argocd-mcp 0.8.0 Authentication Bypass via Unauthenticated HTTP

## Summary
Severity: Critical
Advisory: CVE-2026-82456
Aliases: GHSA-rp45-5x3v-48mr
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-29
Source: https://osv.dev/vulnerability/CVE-2026-82456
Type: osv

## Details
argocd-mcp 0.8.0 binds its HTTP transport to every network interface and accepts MCP sessions without requiring caller credentials when ARGOCD_API_TOKEN is configured. Attackers who can reach the listener can invoke the full tool surface using the operator's stored token to create applications, request syncs, and modify Argo CD resources.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82456.json
- https://github.com/argoproj-labs/mcp-for-argocd/security/advisories/GHSA-rp45-5x3v-48mr
- https://nvd.nist.gov/vuln/detail/CVE-2026-82456
- https://www.vulncheck.com/advisories/argocd-mcp-0.8.0-authentication-bypass-via-unauthenticated-http
- https://github.com/argoproj-labs/mcp-for-argocd
