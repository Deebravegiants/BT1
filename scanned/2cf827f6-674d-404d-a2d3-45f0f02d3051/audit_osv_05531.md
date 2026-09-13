# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-18433
Aliases: CVE-2026-18433
Ecosystem: Bitnami
Published: 2026-08-18
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-18433
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.2.0 <19.2.2

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 19.1 before 19.1.4 and 19.2 before 19.2.2 that under certain conditions could have allowed an authenticated user to read policy configuration belonging to a namespace they were not authorized to access, due to incorrect authorization checks in a GraphQL query.

## References
- https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-2-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/607556
- https://hackerone.com/reports/3776182
- https://nvd.nist.gov/vuln/detail/CVE-2026-18433
