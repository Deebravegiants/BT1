# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-6336
Aliases: CVE-2026-6336
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-6336
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.2.0 <19.2.1

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 16.6 before 19.0.5, 19.1 before 19.1.3, and 19.2 before 19.2.1 that under certain conditions could have allowed an unauthorized user to view project import source information due to a missing authorization check.

## References
- https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-2-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/596762
- https://hackerone.com/reports/3661988
- https://nvd.nist.gov/vuln/detail/CVE-2026-6336
