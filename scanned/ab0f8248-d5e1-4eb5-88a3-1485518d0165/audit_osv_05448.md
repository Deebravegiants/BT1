# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-4006
Aliases: CVE-2024-4006
Ecosystem: Bitnami
Published: 2024-04-27
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-4006
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.11.0 <16.11.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 16.7 before 16.9.6, all versions starting from 16.10 before 16.10.4, all versions starting from 16.11 before 16.11.1 where personal access scopes were not honored by GraphQL subscriptions

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/455805
- https://nvd.nist.gov/vuln/detail/CVE-2024-4006
