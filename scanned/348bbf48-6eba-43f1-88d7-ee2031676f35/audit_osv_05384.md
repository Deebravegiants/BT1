# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-3443
Aliases: CVE-2023-3443
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-3443
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.6.0 <16.6.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 12.1 before 16.4.3, all versions starting from 16.5 before 16.5.3, all versions starting from 16.6 before 16.6.1. It was possible for a Guest user to add an emoji on confidential work items.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/416497
- https://hackerone.com/reports/2036500
- https://nvd.nist.gov/vuln/detail/CVE-2023-3443
