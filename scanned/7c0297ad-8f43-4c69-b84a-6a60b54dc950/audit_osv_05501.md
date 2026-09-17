# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-3396
Aliases: CVE-2025-3396
Ecosystem: Bitnami
Published: 2025-07-16
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-3396
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.1.0 <18.0.1

## Details
An issue has been discovered in GitLab EE affecting all versions from 13.3 before 17.11.6, 18.0 before 18.0.4, and 18.1 before 18.1.2 that could have allowed authenticated project owners to bypass group-level forking restrictions by manipulating API requests.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/534636
- https://hackerone.com/reports/3079956
- https://nvd.nist.gov/vuln/detail/CVE-2025-3396
