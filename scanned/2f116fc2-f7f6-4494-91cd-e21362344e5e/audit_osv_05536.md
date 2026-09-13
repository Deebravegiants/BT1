# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-2726
Aliases: CVE-2026-2726
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-2726
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.10.0 <18.10.1

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 11.10 before 18.8.7, 18.9 before 18.9.3, and 18.10 before 18.10.1 that could have allowed an authenticated user to perform unauthorized actions on merge requests in other projects due to improper access control during cross-repository operations.

## References
- https://about.gitlab.com/releases/2026/03/25/patch-release-gitlab-18-10-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/590717
- https://hackerone.com/reports/3543886
- https://nvd.nist.gov/vuln/detail/CVE-2026-2726
