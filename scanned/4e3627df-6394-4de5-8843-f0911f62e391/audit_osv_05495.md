# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-14595
Aliases: CVE-2025-14595
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-14595
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.10.0 <18.10.1

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 18.6 before 18.8.7, 18.9 before 18.9.3, and 18.10 before 18.10.1 that under certain conditions could have allowed an authenticated user with Planner role to view security category metadata and attributes in group security configuration due to improper access control

## References
- https://about.gitlab.com/releases/2026/03/25/patch-release-gitlab-18-10-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/583971
- https://hackerone.com/reports/3457779
- https://nvd.nist.gov/vuln/detail/CVE-2025-14595
