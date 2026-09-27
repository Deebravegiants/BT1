# [M] BIT-gitlab-2021-39872

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39872
Aliases: CVE-2021-39872
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39872
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.3.0 <14.3.1

## Details
In all versions of GitLab CE/EE since version 14.1, an improper access control vulnerability allows users with expired password to still access GitLab through git and API through access tokens acquired before password expiration.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39872.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/337954
- https://hackerone.com/reports/1285226
- https://nvd.nist.gov/vuln/detail/CVE-2021-39872
