# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-8116
Aliases: CVE-2024-8116
Ecosystem: Bitnami
Published: 2024-12-18
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-8116
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.6.0 <17.6.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions from 16.9 before 17.4.6, 17.5 before 17.5.4, and 17.6 before 17.6.2. By using a specific GraphQL query, under specific conditions an unauthorized user can retrieve branch names.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/480509
- https://hackerone.com/reports/2666216
- https://nvd.nist.gov/vuln/detail/CVE-2024-8116
