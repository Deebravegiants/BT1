# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-2601
Aliases: CVE-2026-2601
Ecosystem: Bitnami
Published: 2026-05-28
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-2601
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.0.0 <19.0.2

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 11.5 before 18.10.7, 18.11 before 18.11.4, and 19.0 before 19.0.1 that under certain conditions could have allowed an authenticated user with developer-role permissions to access sensitive deployment data on projects due to improper authorization checks.

## References
- https://about.gitlab.com/releases/2026/05/27/patch-release-gitlab-19-0-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/590389
- https://hackerone.com/reports/3556381
- https://nvd.nist.gov/vuln/detail/CVE-2026-2601
