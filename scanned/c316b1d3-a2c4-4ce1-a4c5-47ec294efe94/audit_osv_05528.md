# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-1752
Aliases: CVE-2026-1752
Ecosystem: Bitnami
Published: 2026-04-17
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-1752
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.10.0 <18.10.3

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 11.3 before 18.8.9, 18.9 before 18.9.5, and 18.10 before 18.10.3 that could have allowed an authenticated user with developer-role permissions to modify protected environment settings due to improper authorization checks in the API.

## References
- https://about.gitlab.com/releases/2026/04/08/patch-release-gitlab-18-10-3-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/588413
- https://hackerone.com/reports/3533545
- https://nvd.nist.gov/vuln/detail/CVE-2026-1752
