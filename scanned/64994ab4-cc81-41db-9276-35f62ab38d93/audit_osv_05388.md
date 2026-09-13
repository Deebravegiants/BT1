# [H] Improper Validation of Specified Type of Input in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2023-3900
Aliases: CVE-2023-3900
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-3900
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.2.0 <16.2.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 16.1 before 16.1.3, all versions starting from 16.2 before 16.2.2. An invalid 'start_sha' value on merge requests page may lead to Denial of Service as Changes tab would not load.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/418770
- https://hackerone.com/reports/2058514
- https://nvd.nist.gov/vuln/detail/CVE-2023-3900
