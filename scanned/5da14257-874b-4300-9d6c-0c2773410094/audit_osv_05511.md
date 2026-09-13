# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-9825
Aliases: CVE-2025-9825
Ecosystem: Bitnami
Published: 2025-11-25
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-9825
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.4.0 <18.4.2

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 13.7 to 18.2.8, 18.3 before 18.3.4, and 18.4 before 18.4.2 that could have allowed authenticated users without project membership to view sensitive manual CI/CD variables by querying the GraphQL API.

## References
- https://about.gitlab.com/releases/2025/10/08/patch-release-gitlab-18-4-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/567301
- https://hackerone.com/reports/3319800
- https://nvd.nist.gov/vuln/detail/CVE-2025-9825
