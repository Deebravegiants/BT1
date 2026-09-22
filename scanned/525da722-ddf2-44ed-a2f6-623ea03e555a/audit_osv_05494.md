# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-14592
Aliases: CVE-2025-14592
Ecosystem: Bitnami
Published: 2026-02-16
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-14592
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.8.0 <18.8.4

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 18.6 before 18.6.6, 18.7 before 18.7.4, and 18.8 before 18.8.4 that, under certain conditions could have allowed an authenticated user to perform unauthorized operations by submitting GraphQL mutations through the GLQL API endpoint.

## References
- https://about.gitlab.com/releases/2026/02/10/patch-release-gitlab-18-8-4-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/583961
- https://hackerone.com/reports/3451435
- https://nvd.nist.gov/vuln/detail/CVE-2025-14592
