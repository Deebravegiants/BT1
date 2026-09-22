# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-0120
Aliases: CVE-2023-0120
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-0120
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.3.0 <16.3.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 10.0 before 16.1.5, all versions starting from 16.2 before 16.2.5, all versions starting from 16.3 before 16.3.1. Due to improper permission validation it was possible to edit labels description by an unauthorised user.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/387531
- https://hackerone.com/reports/1818425
- https://nvd.nist.gov/vuln/detail/CVE-2023-0120
