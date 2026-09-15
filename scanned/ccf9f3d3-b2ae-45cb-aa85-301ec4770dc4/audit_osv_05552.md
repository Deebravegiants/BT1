# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-6883
Aliases: CVE-2026-6883
Ecosystem: Bitnami
Published: 2026-05-18
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-6883
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.11.0 <18.11.3

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 15.7 before 18.9.7, 18.10 before 18.10.6, and 18.11 before 18.11.3 that could have allowed an authenticated user to bypass merge request approval requirements due to improper cleanup of orphaned policy records.

## References
- https://about.gitlab.com/releases/2026/05/13/patch-release-gitlab-18-11-3-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/596350
- https://nvd.nist.gov/vuln/detail/CVE-2026-6883
