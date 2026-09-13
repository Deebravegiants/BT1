# [M] Incorrect User Management in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-3115
Aliases: CVE-2023-3115
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-3115
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.4.0 <16.4.1

## Details
An issue has been discovered in GitLab EE affecting all versions affecting all versions from 11.11 prior to 16.2.8, 16.3 prior to 16.3.5, and 16.4 prior to 16.4.1. Single Sign On restrictions were not correctly enforced for indirect project members accessing public members-only project repositories.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/414367
- https://hackerone.com/reports/2004158
- https://nvd.nist.gov/vuln/detail/CVE-2023-3115
