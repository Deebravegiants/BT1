# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-4317
Aliases: CVE-2023-4317
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-4317
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.6.0 <16.6.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 9.2 before 16.4.3, all versions starting from 16.5 before 16.5.3, all versions starting from 16.6 before 16.6.1. It was possible for a user with the Developer role to update a pipeline schedule from an unprotected branch to a protected branch.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/421846
- https://hackerone.com/reports/2089517
- https://nvd.nist.gov/vuln/detail/CVE-2023-4317
