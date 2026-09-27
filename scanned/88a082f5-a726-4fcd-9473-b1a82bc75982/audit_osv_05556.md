# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-8667
Aliases: CVE-2026-8667
Ecosystem: Bitnami
Published: 2026-08-18
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-8667
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.2.0 <19.2.2

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 17.6 before 19.0.6, 19.1 before 19.1.4, and 19.2 before 19.2.2  that under certain conditions could have allowed an authenticated user with developer role to modify certain package registry metadata without the required maintainer-level permissions due to improper authorization checks.

## References
- https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-2-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/600228
- https://hackerone.com/reports/3598070
- https://nvd.nist.gov/vuln/detail/CVE-2026-8667
