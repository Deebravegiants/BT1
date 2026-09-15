# [M] Kanboard has Authenticated SQL Injection in Project Permissions Handler

## Summary
Severity: Medium
Advisory: CVE-2026-33058
Aliases: GHSA-f62r-m4mr-2xhh
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-33058
Type: osv

## Details
Kanboard is project management software focused on Kanban methodology. Versions prior to 1.2.51 have an authenticated SQL injection vulnerability. Attackers with the permission to add users to a project can leverage this vulnerability to dump the entirety of the kanboard database. Version 1.2.51 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33058.json
- https://github.com/kanboard/kanboard/security/advisories/GHSA-f62r-m4mr-2xhh
- https://nvd.nist.gov/vuln/detail/CVE-2026-33058
