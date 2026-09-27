# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-12704
Aliases: CVE-2025-12704
Ecosystem: Bitnami
Published: 2026-03-13
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-12704
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.9.0 <18.9.2

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 18.2 before 18.7.6, 18.8 before 18.8.6, and 18.9 before 18.9.2 that could have allowed an authenticated user to access Virtual Registry data in groups where they are not members due to improper authorization under certain conditions.

## References
- https://about.gitlab.com/releases/2026/03/11/patch-release-gitlab-18-9-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/579534
- https://hackerone.com/reports/3389825
- https://nvd.nist.gov/vuln/detail/CVE-2025-12704
