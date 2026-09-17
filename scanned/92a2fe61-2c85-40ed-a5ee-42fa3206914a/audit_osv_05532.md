# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-2238
Aliases: CVE-2026-2238
Ecosystem: Bitnami
Published: 2026-06-29
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-2238
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.1.0 <19.1.1

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 17.5 before 18.11.6, 19.0 before 19.0.3, and 19.1 before 19.1.1 that under certain conditions could have allowed an unauthenticated user to view confidential issue references on public projects due to improper authorization checks.

## References
- https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-1-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/589186
- https://hackerone.com/reports/3543011
- https://nvd.nist.gov/vuln/detail/CVE-2026-2238
