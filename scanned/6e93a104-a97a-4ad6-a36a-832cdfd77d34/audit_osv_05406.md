# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-5061
Aliases: CVE-2023-5061
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-5061
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.6.0 <16.6.2

## Details
An issue has been discovered in GitLab affecting all versions starting from 9.3 before 16.4.4, all versions starting from 16.5 before 16.5.4, all versions starting from 16.6 before 16.6.2. In certain situations, it may have been possible for developers to override predefined CI variables via the REST API.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/425521
- https://hackerone.com/reports/2125189
- https://nvd.nist.gov/vuln/detail/CVE-2023-5061
