# [H] Incorrect Authorization in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2025-13928
Aliases: CVE-2025-13928
Ecosystem: Bitnami
Published: 2026-01-27
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-13928
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.8.0 <18.8.2

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 17.7 before 18.6.4, 18.7 before 18.7.2, and 18.8 before 18.8.2 that could have allowed an unauthenticated user to cause a denial of service condition by exploiting incorrect authorization validation in API endpoints.

## References
- https://about.gitlab.com/releases/2026/01/21/patch-release-gitlab-18-8-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/582736
- https://hackerone.com/reports/3439441
- https://nvd.nist.gov/vuln/detail/CVE-2025-13928
