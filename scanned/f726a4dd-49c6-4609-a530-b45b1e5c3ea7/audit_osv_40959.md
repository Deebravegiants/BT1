# [H] Capgo - Insufficient Authentication in Email Change Endpoint

## Summary
Severity: High
Advisory: CVE-2026-56308
Aliases: GHSA-9px4-w25f-mvm4
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-12
Source: https://osv.dev/vulnerability/CVE-2026-56308
Type: osv

## Details
Capgo before 12.128.2 allows email address changes without requiring current password re-authentication or verification of the existing email address. An attacker with access to a valid session cookie or authenticated browser can change the account email to gain control of account recovery and bypass multi-factor authentication protections.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56308.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-9px4-w25f-mvm4
- https://nvd.nist.gov/vuln/detail/CVE-2026-56308
- https://www.vulncheck.com/advisories/capgo-insufficient-authentication-in-email-change-endpoint
