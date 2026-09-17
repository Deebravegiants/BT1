# [C] Origin Validation Error in GitLab

## Summary
Severity: Critical
Advisory: BIT-gitlab-2025-7659
Aliases: CVE-2025-7659
Ecosystem: Bitnami
Published: 2026-02-16
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-7659
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.8.0 <18.8.4

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 18.2 before 18.6.6, 18.7 before 18.7.4, and 18.8 before 18.8.4 that could have allowed an unauthenticated user to steal tokens and access private repositories by abusing incomplete validation in the Web IDE.

## References
- https://about.gitlab.com/releases/2026/02/10/patch-release-gitlab-18-8-4-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/555440
- https://hackerone.com/reports/3234976
- https://nvd.nist.gov/vuln/detail/CVE-2025-7659
