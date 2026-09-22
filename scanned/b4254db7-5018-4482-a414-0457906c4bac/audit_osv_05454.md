# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-5318
Aliases: CVE-2024-5318
Ecosystem: Bitnami
Published: 2024-05-29
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-5318
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.0.0 <17.0.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 11.11 prior to 16.10.6, starting from 16.11 prior to 16.11.3, and starting from 17.0 prior to 17.0.1. A Guest user can view dependency lists of private projects through job artifacts.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/427526
- https://hackerone.com/reports/2189464
- https://nvd.nist.gov/vuln/detail/CVE-2024-5318
