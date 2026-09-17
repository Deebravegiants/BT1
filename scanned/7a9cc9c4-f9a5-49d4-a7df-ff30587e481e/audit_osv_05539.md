# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-4672
Aliases: CVE-2026-4672
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-4672
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.2.0 <19.2.1

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 18.4 before 19.0.5, 19.1 before 19.1.3, and 19.2 before 19.2.1 that under certain conditions could have allowed an authenticated user with guest-role permissions to access test report contents they were not authorized to view due to improper access control enforcement.

## References
- https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-2-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/594528
- https://hackerone.com/reports/3617676
- https://nvd.nist.gov/vuln/detail/CVE-2026-4672
