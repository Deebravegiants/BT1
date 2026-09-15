# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-14341
Aliases: CVE-2026-14341
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-14341
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.2.0 <19.2.1

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 12.8 before 19.0.5, 19.1 before 19.1.3, and 19.2 before 19.2.1 that under certain conditions could have allowed an authenticated user with Maintainer role to modify protected branch configuration due to improper authorization in a projects API endpoint.

## References
- https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-2-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/604665
- https://hackerone.com/reports/3807593
- https://nvd.nist.gov/vuln/detail/CVE-2026-14341
