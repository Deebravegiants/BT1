# [M] BIT-gitlab-2021-39919

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39919
Aliases: CVE-2021-39919
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39919
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.5.0 <14.5.2

## Details
In all versions of GitLab CE/EE starting version 14.0 before 14.3.6, all versions starting from 14.4 before 14.4.4, all versions starting from 14.5 before 14.5.2, the reset password token and new user email token are accidentally logged which may lead to information disclosure.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39919.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/342445
- https://nvd.nist.gov/vuln/detail/CVE-2021-39919
