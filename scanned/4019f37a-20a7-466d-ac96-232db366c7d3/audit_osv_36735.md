# [M] Kanboard TaskCreationController::duplicateProjects() endpoint does not validate user permissions for target projects

## Summary
Severity: Medium
Advisory: CVE-2026-25531
Aliases: GHSA-vrm3-3337-whp9
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-02-13
Source: https://osv.dev/vulnerability/CVE-2026-25531
Type: osv

## Details
Kanboard is project management software focused on Kanban methodology. Prior to 1.2.50, The fix for CVE-2023-33968 is incomplete. The TaskCreationController::duplicateProjects() endpoint does not validate user permissions for target projects, allowing authenticated users to duplicate tasks into projects they cannot access. This vulnerability is fixed in 1.2.50.

## References
- https://github.com/kanboard/kanboard/releases/tag/v1.2.50
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25531.json
- https://github.com/kanboard/kanboard/security/advisories/GHSA-vrm3-3337-whp9
- https://nvd.nist.gov/vuln/detail/CVE-2026-25531
- https://github.com/kanboard/kanboard/commit/df7b7a21ee071f36466d8b38e40d0b0b8b8d394d
