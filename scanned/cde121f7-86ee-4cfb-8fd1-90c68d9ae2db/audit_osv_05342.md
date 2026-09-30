# [M] BIT-gitlab-2023-1071

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-1071
Aliases: CVE-2023-1071
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-1071
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.10.0 <15.10.1

## Details
An issue has been discovered in GitLab affecting all versions from 15.5 before 15.8.5, all versions starting from 15.9 before 15.9.4, all versions starting from 15.10 before 15.10.1. Due to improper permissions checks it was possible for an unauthorised user to remove an issue from an epic.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-1071.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/385434
- https://nvd.nist.gov/vuln/detail/CVE-2023-1071
