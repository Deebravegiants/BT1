# [M] Exposure of Sensitive Information Through Metadata in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-14351
Aliases: CVE-2026-14351
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-14351
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.2.0 <19.2.1

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 8.8 before 19.0.5, 19.1 before 19.1.3, and 19.2 before 19.2.1 that under certain conditions could have allowed an unauthenticated user to view the title of a confidential issue through a publicly accessible merge request due to improper authorization checks.

## References
- https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-2-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/604691
- https://hackerone.com/reports/3708242
- https://nvd.nist.gov/vuln/detail/CVE-2026-14351
