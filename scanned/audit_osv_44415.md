# [H] Budibase before 3.41.3 Missing Authorization License Management

## Summary
Severity: High
Advisory: CVE-2026-82245
Aliases: GHSA-4wr8-5c3p-rjcr
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82245
Type: osv

## Details
Budibase before 3.41.3 fails to enforce role-based authorization on license management endpoints, allowing any authenticated user to delete license keys or manipulate offline tokens. Attackers with basic user privileges can access /api/global/license/* endpoints to disable premium features and downgrade deployments for all users.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-4wr8-5c3p-rjcr
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82245.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82245
- https://www.vulncheck.com/advisories/budibase-before-3.41.3-missing-authorization-license-management
