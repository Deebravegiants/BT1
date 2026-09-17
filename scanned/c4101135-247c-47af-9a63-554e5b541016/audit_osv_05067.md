# [M] BIT-gitlab-2021-22237

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-22237
Aliases: CVE-2021-22237
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22237
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.1.0 <14.1.2

## Details
Under specialized conditions, GitLab may allow a user with an impersonation token to perform Git actions even if impersonation is disabled. This vulnerability is present in GitLab CE/EE versions before 13.12.9, 14.0.7, 14.1.2

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22237.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/297516
- https://nvd.nist.gov/vuln/detail/CVE-2021-22237
