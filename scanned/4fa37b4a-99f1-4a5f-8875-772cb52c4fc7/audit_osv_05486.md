# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-12555
Aliases: CVE-2025-12555
Ecosystem: Bitnami
Published: 2026-03-13
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-12555
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.9.0 <18.9.2

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 15.1 before 18.7.6, 18.8 before 18.8.6, and 18.9 before 18.9.2 that, under certain conditions, could have allowed an authenticated user to access previous pipeline job information on projects with repository and CI/CD disabled due to improper authorization checks.

## References
- https://about.gitlab.com/releases/2026/03/11/patch-release-gitlab-18-9-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/579126
- https://hackerone.com/reports/3354642
- https://nvd.nist.gov/vuln/detail/CVE-2025-12555
