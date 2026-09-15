# [C] Kimai before 2.57.0 Improper Authorization via Favorite Endpoints

## Summary
Severity: Critical
Advisory: CVE-2026-80197
Aliases: GHSA-j5mc-p8qg-39j7
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-80197
Type: osv

## Details
Kimai before 2.57.0 contains an improper authorization vulnerability in the favorite timesheet add and remove endpoints that allows authenticated users to manipulate other users' bookmarks. Attackers can add or remove timesheet entries from another user's favorite list by referencing their timesheet identifier, enabling cross-user business-state tampering without administrative privileges.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80197.json
- https://github.com/kimai/kimai/security/advisories/GHSA-j5mc-p8qg-39j7
- https://nvd.nist.gov/vuln/detail/CVE-2026-80197
- https://www.vulncheck.com/advisories/kimai-before-2.57.0-improper-authorization-via-favorite-endpoints
