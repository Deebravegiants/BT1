# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-6269
Aliases: CVE-2026-6269
Ecosystem: Bitnami
Published: 2026-06-13
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-6269
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.0.0 <19.0.2

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 15.10 before 18.10.8, 18.11 before 18.11.5, and 19.0 before 19.0.2 that under certain conditions could have allowed an authenticated user with developer-role permissions to modify hidden merge requests due to incorrect authorization enforcements.

## References
- https://about.gitlab.com/releases/2026/06/10/patch-release-gitlab-19-0-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/596625
- https://hackerone.com/reports/3661880
- https://nvd.nist.gov/vuln/detail/CVE-2026-6269
