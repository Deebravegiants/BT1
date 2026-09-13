# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-2022
Aliases: CVE-2023-2022
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-2022
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.2.0 <16.2.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting before 16.0.8, all versions starting from 16.1 before 16.1.3, all versions starting from 16.2 before 16.2.2, which leads to developers being able to create pipeline schedules on protected branches even if they don't have access to merge

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/407166
- https://hackerone.com/reports/1936572
- https://nvd.nist.gov/vuln/detail/CVE-2023-2022
