# [C] Kimai before 2.62.0 Authorization Bypass via QuickEntry

## Summary
Severity: Critical
Advisory: CVE-2026-80193
Aliases: GHSA-2w7f-x78f-89q2
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-80193
Type: osv

## Details
Kimai before 2.62.0 fails to validate create_other_timesheet permission in the QuickEntry controller when creating new timesheets. Authenticated users with view_other_timesheet and edit_other_timesheet permissions can create timesheet records for team members by submitting the QuickEntry form, bypassing authorization checks enforced elsewhere.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80193.json
- https://github.com/kimai/kimai/security/advisories/GHSA-2w7f-x78f-89q2
- https://nvd.nist.gov/vuln/detail/CVE-2026-80193
- https://www.vulncheck.com/advisories/kimai-before-2.62.0-authorization-bypass-via-quickentry
