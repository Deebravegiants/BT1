# [M] Capgo - Two-Factor Authentication Bypass via Organization Management API

## Summary
Severity: Medium
Advisory: CVE-2026-56256
Aliases: GHSA-cww4-5xfp-jw98
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-56256
Type: osv

## Details
Capgo before 12.128.2 enforces mandatory two-factor authentication only at the UI level. Sensitive Organization (ORG) management API endpoints (e.g., editing organization details, inviting users) do not validate 2FA completion on the backend. An authenticated Admin user who has not enabled 2FA can replay or modify a previously captured ORG API request to perform privileged organization actions, bypassing the globally enforced 2FA requirement.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56256.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-cww4-5xfp-jw98
- https://nvd.nist.gov/vuln/detail/CVE-2026-56256
- https://www.vulncheck.com/advisories/capgo-two-factor-authentication-bypass-via-organization-management-api
