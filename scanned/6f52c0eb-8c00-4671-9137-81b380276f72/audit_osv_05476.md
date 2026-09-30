# [M] Improper Validation of Specified Quantity in Input in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-10094
Aliases: CVE-2025-10094
Ecosystem: Bitnami
Published: 2025-09-16
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-10094
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.3.0 <18.3.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions from 10.7 before 18.1.6, 18.2 before 18.2.6, and 18.3 before 18.3.2 that could have allowed authenticated users to disrupt access to token listings and related administrative operations by creating tokens with excessively large names.

## References
- https://about.gitlab.com/releases/2025/09/10/patch-release-gitlab-18-3-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/528469
- https://hackerone.com/reports/3049089
- https://nvd.nist.gov/vuln/detail/CVE-2025-10094
