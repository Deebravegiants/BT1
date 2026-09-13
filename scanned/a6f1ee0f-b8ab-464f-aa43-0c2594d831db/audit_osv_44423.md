# [H] Gophish Account Lockout and Forced Password Change Bypassable via API Key

## Summary
Severity: High
Advisory: CVE-2026-82269
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82269
Type: osv

## Details
Gophish through 0.12.1 fails to enforce account lockout and password change requirements in the API authentication middleware. Attackers with valid API keys can bypass these security controls and retain full API access even when their account is locked or password change is required.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82269.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82269
- https://www.vulncheck.com/advisories/gophish-account-lockout-and-forced-password-change-bypassable-via-api-key
- https://github.com/gophish/gophish/issues/9440
- https://github.com/gophish/gophish
- https://github.com/gophish/gophish/blob/95618469799295e2c0fec980805a2dfbb818816b/middleware/middleware.go
