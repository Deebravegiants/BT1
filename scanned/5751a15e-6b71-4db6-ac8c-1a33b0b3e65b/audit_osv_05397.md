# [M] Direct Request ('Forced Browsing') in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-4018
Aliases: CVE-2023-4018
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-4018
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.3.0 <16.3.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 16.2 before 16.2.5, all versions starting from 16.3 before 16.3.1. Due to improper permission validation it was possible to create model experiments in public projects.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/420301
- https://hackerone.com/reports/2083440
- https://nvd.nist.gov/vuln/detail/CVE-2023-4018
