# [M] Access Control Check Implemented After Asset is Accessed in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-3607
Aliases: CVE-2026-3607
Ecosystem: Bitnami
Published: 2026-05-18
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-3607
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.11.0 <18.11.3

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 18.3 before 18.9.7, 18.10 before 18.10.6, and 18.11 before 18.11.3 that could have allowed an authenticated user with developer-role permissions to bypass package protection rules due to improper access control.

## References
- https://about.gitlab.com/releases/2026/05/13/patch-release-gitlab-18-11-3-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/592466
- https://hackerone.com/reports/3586233
- https://nvd.nist.gov/vuln/detail/CVE-2026-3607
