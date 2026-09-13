# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-2576
Aliases: CVE-2023-2576
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-2576
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.1.0 <16.1.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 13.7 before 15.11.10, all versions starting from 16.0 before 16.0.6, all versions starting from 16.1 before 16.1.1. This allowed a developer to remove the CODEOWNERS rules and merge to a protected branch.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/410123
- https://hackerone.com/reports/1898054
- https://nvd.nist.gov/vuln/detail/CVE-2023-2576
