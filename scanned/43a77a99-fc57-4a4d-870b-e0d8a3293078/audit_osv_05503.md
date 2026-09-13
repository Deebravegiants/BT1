# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-5315
Aliases: CVE-2025-5315
Ecosystem: Bitnami
Published: 2025-06-30
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-5315
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.1.0 <18.0.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions from 17.2 before 17.11.5, 18.0 before 18.0.3, and 18.1 before 18.1.1 that could have allowed authenticated users with Guest role permissions to add child items to incident work items by sending crafted API requests that bypassed UI-enforced role restrictions.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/546282
- https://hackerone.com/reports/3163037
- https://nvd.nist.gov/vuln/detail/CVE-2025-5315
