# [M] Exposure of Sensitive Information to an Unauthorized Actor in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-4343
Aliases: CVE-2022-4343
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-4343
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.3.0 <16.3.1

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 13.12 before 16.1.5, all versions starting from 16.2 before 16.2.5, all versions starting from 16.3 before 16.3.1 in which a project member can leak credentials stored in site profile.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/385124
- https://hackerone.com/reports/1767797
- https://nvd.nist.gov/vuln/detail/CVE-2022-4343
