# [M] BIT-gitlab-2023-0485

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-0485
Aliases: CVE-2023-0485
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-0485
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.10.0 <15.10.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 13.11 before 15.8.5, all versions starting from 15.9 before 15.9.4, all versions starting from 15.10 before 15.10.1. It was possible that a project member demoted to a user role to read project updates by doing a diff with a pre-existing fork.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-0485.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/389191
- https://hackerone.com/reports/1837937
- https://nvd.nist.gov/vuln/detail/CVE-2023-0485
