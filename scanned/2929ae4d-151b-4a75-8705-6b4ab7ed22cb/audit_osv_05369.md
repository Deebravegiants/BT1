# [M] Authorization Bypass Through User-Controlled Key in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-2190
Aliases: CVE-2023-2190
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-2190
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.1.0 <16.1.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 13.10 before 15.11.10, all versions starting from 16.0 before 16.0.6, all versions starting from 16.1 before 16.1.1. It may be possible for users to view new commits to private projects in a fork created while the project was public.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/408137
- https://hackerone.com/reports/1944500
- https://nvd.nist.gov/vuln/detail/CVE-2023-2190
