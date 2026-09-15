# [M] OpenProject has a Permission Check bypass on Budget deletion allows reassignment of WorkPackages into other budgets

## Summary
Severity: Medium
Advisory: CVE-2026-30239
Aliases: GHSA-gpvh-g967-g4h8
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-30239
Type: osv

## Details
OpenProject is an open-source, web-based project management software. Prior to 17.2.0, when budgets are deleted, the work packages that were assigned to this budget need to be moved to a different budget. This action was performed before the permission check on the delete action was executed. This allowed all users in the application to delete work package budget assignments. This vulnerability is fixed in 17.2.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30239.json
- https://github.com/opf/openproject/security/advisories/GHSA-gpvh-g967-g4h8
- https://nvd.nist.gov/vuln/detail/CVE-2026-30239
