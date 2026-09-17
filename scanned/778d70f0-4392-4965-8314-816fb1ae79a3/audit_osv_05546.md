# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-5952
Aliases: CVE-2026-5952
Ecosystem: Bitnami
Published: 2026-06-29
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-5952
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.1.0 <19.1.1

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 17.11 before 18.11.6, 19.0 before 19.0.3, and 19.1 before 19.1.1 that under certain conditions could have allowed an authenticated user with developer-role permissions to bypass package protection rules and overwrite protected Maven package metadata due to incorrect authorization checks.

## References
- https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-1-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/596134
- https://hackerone.com/reports/3632428
- https://nvd.nist.gov/vuln/detail/CVE-2026-5952
