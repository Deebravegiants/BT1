# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-3509
Aliases: CVE-2023-3509
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-3509
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.9.0 <16.9.1

## Details
An issue has been discovered in GitLab affecting all versions before 16.7.6, all versions starting from 16.8 before 16.8.3, all versions starting from 16.9 before 16.9.1. It was possible for group members with sub-maintainer role to change the title of privately accessible deploy keys associated with projects in the group.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/416945
- https://hackerone.com/reports/2037814
- https://nvd.nist.gov/vuln/detail/CVE-2023-3509
