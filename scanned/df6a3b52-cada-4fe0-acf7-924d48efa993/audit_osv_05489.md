# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-1299
Aliases: CVE-2025-1299
Ecosystem: Bitnami
Published: 2025-07-29
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-1299
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.2.0 <18.2.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 15.4 before 18.0.5, all versions starting from 18.1 before 18.1.3, all versions starting from 18.2 before 18.2.1 that, under circumstances, could have allowed an unauthorized user to read deployment job logs by sending a crafted request.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/519696
- https://hackerone.com/reports/2969145
- https://nvd.nist.gov/vuln/detail/CVE-2025-1299
