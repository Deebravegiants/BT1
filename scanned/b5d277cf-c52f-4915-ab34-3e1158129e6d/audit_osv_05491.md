# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-13781
Aliases: CVE-2025-13781
Ecosystem: Bitnami
Published: 2026-01-13
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-13781
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.7.0 <18.7.1

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 18.5 before 18.5.5, 18.6 before 18.6.3, and 18.7 before 18.7.1 that could have allowed an authenticated user to modify instance-wide AI feature provider settings by exploiting missing authorization checks in GraphQL mutations.

## References
- https://about.gitlab.com/releases/2026/01/07/patch-release-gitlab-18-7-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/578756
- https://hackerone.com/reports/3400940
- https://nvd.nist.gov/vuln/detail/CVE-2025-13781
