# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-5198
Aliases: CVE-2023-5198
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-5198
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.4.0 <16.4.1

## Details
An issue has been discovered in GitLab affecting all versions prior to 16.2.7, all versions starting from 16.3 before 16.3.5, and all versions starting from 16.4 before 16.4.1. It was possible for a removed project member to write to protected branches using deploy keys.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/416957
- https://hackerone.com/reports/2041789
- https://nvd.nist.gov/vuln/detail/CVE-2023-5198
