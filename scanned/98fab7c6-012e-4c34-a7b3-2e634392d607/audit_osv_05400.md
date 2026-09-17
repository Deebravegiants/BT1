# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-4532
Aliases: CVE-2023-4532
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-4532
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.4.0 <16.4.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 16.2 before 16.2.8, all versions starting from 16.3 before 16.3.5, all versions starting from 16.4 before 16.4.1. Users were capable of linking CI/CD jobs of private projects which they are not a member of.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/423357
- https://hackerone.com/reports/2084199
- https://nvd.nist.gov/vuln/detail/CVE-2023-4532
