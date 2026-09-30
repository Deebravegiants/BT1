# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-6277
Aliases: CVE-2026-6277
Ecosystem: Bitnami
Published: 2026-06-12
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-6277
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.0.0 <19.0.2

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 13.9 before 18.10.8, 18.11 before 18.11.5, and 19.0 before 19.0.2 that under certain conditions could have allowed an authenticated user with Security Manager-role permissions to manage project security configuration even when the relevant feature was in a disabled state, due to incorrect authorization enforcement.

## References
- https://about.gitlab.com/releases/2026/06/10/patch-release-gitlab-19-0-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/596656
- https://hackerone.com/reports/3662615
- https://nvd.nist.gov/vuln/detail/CVE-2026-6277
