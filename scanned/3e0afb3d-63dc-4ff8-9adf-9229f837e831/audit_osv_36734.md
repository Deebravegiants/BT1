# [M] Kanboard is missing authorization check in getSwimlane API allows cross-project data access

## Summary
Severity: Medium
Advisory: CVE-2026-25530
Aliases: GHSA-6rxw-vvvj-r93q
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-02-10
Source: https://osv.dev/vulnerability/CVE-2026-25530
Type: osv

## Details
Kanboard is project management software focused on Kanban methodology. Prior to 1.2.50, the getSwimlane API method lacks project-level authorization, allowing authenticated users to access swimlane data from projects they cannot access. This vulnerability is fixed in 1.2.50.

## References
- https://github.com/kanboard/kanboard/releases/tag/v1.2.50
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25530.json
- https://github.com/kanboard/kanboard/security/advisories/GHSA-6rxw-vvvj-r93q
- https://nvd.nist.gov/vuln/detail/CVE-2026-25530
- https://github.com/kanboard/kanboard/commit/c3d8d20e05322b09e036fed7afb57194d624a414
