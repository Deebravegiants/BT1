# [C] Ech0 before 4.5.1 Authorization Bypass via Session Tokens

## Summary
Severity: Critical
Advisory: CVE-2026-79665
Aliases: GHSA-hmmq-qh6g-6wgh
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-79665
Type: osv

## Details
Ech0 before 4.5.1 contains an authorization bypass vulnerability where session tokens skip scope validation in RequireScopes middleware, allowing logged-in non-admin users to access admin endpoints. Attackers can read system logs, visitor statistics, user emails, and subscribe to live WebSocket logs by sending authenticated session tokens to unprotected endpoints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79665.json
- https://github.com/lin-snow/Ech0/security/advisories/GHSA-hmmq-qh6g-6wgh
- https://nvd.nist.gov/vuln/detail/CVE-2026-79665
- https://www.vulncheck.com/advisories/ech0-before-authorization-bypass-via-session-tokens
