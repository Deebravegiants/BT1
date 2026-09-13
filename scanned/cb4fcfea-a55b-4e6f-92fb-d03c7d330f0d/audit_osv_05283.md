# [M] BIT-gitlab-2022-3411

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-3411
Aliases: CVE-2022-3411
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3411
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.8.0 <15.8.1

## Details
A lack of length validation in GitLab CE/EE affecting all versions from 12.4 before 15.6.7, 15.7 before 15.7.6, and 15.8 before 15.8.1 allows an authenticated attacker to create a large Issue description via GraphQL which, when repeatedly requested, saturates CPU usage.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3411.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/376247
- https://hackerone.com/reports/1685995
- https://nvd.nist.gov/vuln/detail/CVE-2022-3411
