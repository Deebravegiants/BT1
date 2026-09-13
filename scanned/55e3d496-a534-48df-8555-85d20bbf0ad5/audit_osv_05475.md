# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-0765
Aliases: CVE-2025-0765
Ecosystem: Bitnami
Published: 2025-07-29
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-0765
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.2.0 <18.2.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions from 17.9 before 18.0.5, 18.1 before 18.1.3, and 18.2 before 18.2.1 that could have allowed an unauthorized user to access custom service desk email addresses.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/515381
- https://hackerone.com/reports/2956315
- https://nvd.nist.gov/vuln/detail/CVE-2025-0765
