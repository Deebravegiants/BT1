# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-4895
Aliases: CVE-2023-4895
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-4895
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.9.0 <16.9.1

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 12.0 to 16.7.6, all versions starting from 16.8 before 16.8.3, all versions starting from 16.9 before 16.9.1. This vulnerability allows for bypassing the 'group ip restriction' settings to access environment details of projects

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/424766
- https://hackerone.com/reports/2134787
- https://nvd.nist.gov/vuln/detail/CVE-2023-4895
