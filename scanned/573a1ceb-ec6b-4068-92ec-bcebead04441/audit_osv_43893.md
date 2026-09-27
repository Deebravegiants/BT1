# [C] Grav before 2.0.14 Privilege Escalation via Group Access Field

## Summary
Severity: Critical
Advisory: CVE-2026-75837
Aliases: GHSA-xhfv-7758-r9hx
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75837
Type: osv

## Details
Grav before 2.0.14 fails to guard the access field in the core group blueprint with the required security@: admin.super restriction. A delegated admin.users operator can save a group with access[admin][super]=true to escalate to super-admin, gaining scheduler and Twig evaluation capabilities.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75837.json
- https://github.com/getgrav/grav/security/advisories/GHSA-xhfv-7758-r9hx
- https://nvd.nist.gov/vuln/detail/CVE-2026-75837
- https://www.vulncheck.com/advisories/grav-before-privilege-escalation-via-group-access-field
