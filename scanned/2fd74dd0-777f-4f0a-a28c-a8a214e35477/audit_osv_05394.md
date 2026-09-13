# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-3979
Aliases: CVE-2023-3979
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-3979
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.4.0 <16.4.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 10.6 before 16.2.8, all versions starting from 16.3 before 16.3.5, all versions starting from 16.4 before 16.4.1. It was possible that upstream members to collaborate with you on your branch get permission to write to the merge request’s source branch.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/419972
- https://hackerone.com/reports/2082560
- https://nvd.nist.gov/vuln/detail/CVE-2023-3979
