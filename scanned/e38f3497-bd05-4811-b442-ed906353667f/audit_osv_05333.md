# [M] BIT-gitlab-2023-0450

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-0450
Aliases: CVE-2023-0450
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-0450
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.10.0 <15.10.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 8.1 to 15.8.5, and from 15.9 to 15.9.4, and from 15.10 to 15.10.1. It was possible to add a branch with an ambiguous name that could be used to social engineer users.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-0450.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/388962
- https://hackerone.com/reports/1831547
- https://nvd.nist.gov/vuln/detail/CVE-2023-0450
