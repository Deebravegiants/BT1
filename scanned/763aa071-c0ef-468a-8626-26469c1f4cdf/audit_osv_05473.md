# [M] Weak Authentication in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-0605
Aliases: CVE-2025-0605
Ecosystem: Bitnami
Published: 2025-05-26
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-0605
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.0.0 <18.0.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions from 16.8 before 17.10.7, 17.11 before 17.11.3, and 18.0 before 18.0.1. Group access controls could allow certain users to bypass two-factor authentication requirements.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/514204
- https://hackerone.com/reports/2919391
- https://nvd.nist.gov/vuln/detail/CVE-2025-0605
