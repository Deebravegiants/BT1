# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-1663
Aliases: CVE-2026-1663
Ecosystem: Bitnami
Published: 2026-03-13
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-1663
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.9.0 <18.9.2

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 14.4 before 18.7.6, 18.8 before 18.8.6, and 18.9 before 18.9.2 that could have allowed an authenticated user with group import permissions to create labels in private projects due to improper authorization validation in the group import process under certain circumstances.

## References
- https://about.gitlab.com/releases/2026/03/11/patch-release-gitlab-18-9-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/588207
- https://hackerone.com/reports/3485548
- https://nvd.nist.gov/vuln/detail/CVE-2026-1663
