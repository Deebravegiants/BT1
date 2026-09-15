# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-2233
Aliases: CVE-2023-2233
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-2233
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.4.0 <16.4.1

## Details
An improper authorization issue has been discovered in GitLab CE/EE affecting all versions starting from 11.8 before 16.2.8, all versions starting from 16.3 before 16.3.5 and all versions starting from 16.4 before 16.4.1. It allows a project reporter to leak the owner's Sentry instance projects.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/408359
- https://hackerone.com/reports/1947211
- https://nvd.nist.gov/vuln/detail/CVE-2023-2233
