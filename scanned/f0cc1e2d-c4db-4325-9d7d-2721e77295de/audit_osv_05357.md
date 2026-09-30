# [M] BIT-gitlab-2023-1787

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-1787
Aliases: CVE-2023-1787
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-1787
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.10.0 <15.10.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 15.9 before 15.9.4, all versions starting from 15.10 before 15.10.1. A search timeout could be triggered if a specific HTML payload was used in the issue description.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-1787.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/394817
- https://nvd.nist.gov/vuln/detail/CVE-2023-1787
