# [H] BIT-gitlab-2021-39937

## Summary
Severity: High
Advisory: BIT-gitlab-2021-39937
Aliases: CVE-2021-39937
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39937
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.5.0 <14.5.2

## Details
A collision in access memoization logic in all versions of GitLab CE/EE before 14.3.6, all versions starting from 14.4 before 14.4.4, all versions starting from 14.5 before 14.5.2, leads to potential elevated privileges in groups and projects under rare circumstances

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39937.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/336802
- https://nvd.nist.gov/vuln/detail/CVE-2021-39937
