# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-5296
Aliases: CVE-2026-5296
Ecosystem: Bitnami
Published: 2026-05-28
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-5296
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.0.0 <19.0.2

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 18.7 before 18.10.7, 18.11 before 18.11.4, and 19.0 before 19.0.1 that when foundational flows were enabled at the group level, could have allowed an authenticated user with developer-role permissions to bypass flow restrictions under certain conditions.

## References
- https://about.gitlab.com/releases/2026/05/27/patch-release-gitlab-19-0-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/595423
- https://hackerone.com/reports/3626303
- https://nvd.nist.gov/vuln/detail/CVE-2026-5296
