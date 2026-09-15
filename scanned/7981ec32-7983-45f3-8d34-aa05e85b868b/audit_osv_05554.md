# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-8144
Aliases: CVE-2026-8144
Ecosystem: Bitnami
Published: 2026-05-15
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-8144
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.11.0 <18.11.3

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 15.1 before 18.9.7, 18.10 before 18.10.6, and 18.11 before 18.11.3 that could have allowed an authenticated user with project membership to enumerate private group members due to missing authorization checks.

## References
- https://about.gitlab.com/releases/2026/05/13/patch-release-gitlab-18-11-3-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/591964
- https://nvd.nist.gov/vuln/detail/CVE-2026-8144
