# [M] BIT-gitlab-2021-22252

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-22252
Aliases: CVE-2021-22252
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22252
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.1.0 <14.1.2

## Details
A confusion between tag and branch names in GitLab CE/EE affecting all versions since 13.7 allowed a Developer to access protected CI variables which should only be accessible to Maintainers

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22252.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/330364
- https://hackerone.com/reports/1186135
- https://nvd.nist.gov/vuln/detail/CVE-2021-22252
