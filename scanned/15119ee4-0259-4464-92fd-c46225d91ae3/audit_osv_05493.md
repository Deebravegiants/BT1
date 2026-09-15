# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-14103
Aliases: CVE-2025-14103
Ecosystem: Bitnami
Published: 2026-03-02
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-14103
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.9.0 <18.9.1

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 17.7 before 18.7.5, 18.8 before 18.8.5, and 18.9 before 18.9.1 that could have allowed an unauthorized user with Developer-role permissions to set pipeline variables for manually triggered jobs under certain conditions.

## References
- https://about.gitlab.com/releases/2026/02/25/patch-release-gitlab-18-9-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/583053
- https://hackerone.com/reports/3448317
- https://nvd.nist.gov/vuln/detail/CVE-2025-14103
