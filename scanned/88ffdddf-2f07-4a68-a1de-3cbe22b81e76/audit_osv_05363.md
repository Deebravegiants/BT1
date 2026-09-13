# [M] Improper Verification of Cryptographic Signature in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-2030
Aliases: CVE-2023-2030
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-2030
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.7.0 <16.7.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions from 12.2 prior to 16.5.6, 16.6 prior to 16.6.4, and 16.7 prior to 16.7.2 in which an attacker could potentially modify the metadata of signed commits.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/407252
- https://hackerone.com/reports/1929929
- https://nvd.nist.gov/vuln/detail/CVE-2023-2030
