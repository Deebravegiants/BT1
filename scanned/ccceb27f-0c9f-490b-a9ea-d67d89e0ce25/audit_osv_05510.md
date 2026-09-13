# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-9484
Aliases: CVE-2025-9484
Ecosystem: Bitnami
Published: 2026-04-13
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-9484
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.10.0 <18.10.3

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 16.6 before 18.8.9, 18.9 before 18.9.5, and 18.10 before 18.10.3 that under certain circumstances could have allowed an authenticated user to have access to other users' email addresses via certain GraphQL queries.

## References
- https://about.gitlab.com/releases/2026/04/08/patch-release-gitlab-18-10-3-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/565363
- https://hackerone.com/reports/3303810
- https://nvd.nist.gov/vuln/detail/CVE-2025-9484
