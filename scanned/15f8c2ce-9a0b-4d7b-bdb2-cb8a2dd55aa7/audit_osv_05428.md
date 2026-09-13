# [M] Insufficient Session Expiration in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-11668
Aliases: CVE-2024-11668
Ecosystem: Bitnami
Published: 2024-11-28
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-11668
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.6.0 <17.6.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions from 16.11 before 17.4.5, 17.5 before 17.5.3, and 17.6 before 17.6.1. Long-lived connections could potentially bypass authentication controls, allowing unauthorized access to streaming results.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/456922
- https://nvd.nist.gov/vuln/detail/CVE-2024-11668
