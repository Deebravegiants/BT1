# [M] BIT-gitlab-2021-22184

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-22184
Aliases: CVE-2021-22184
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22184
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.8.0 <13.8.2

## Details
An information disclosure issue in GitLab starting from version 12.8 allowed a user with access to the server logs to see sensitive information that wasn't properly redacted.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22184.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/281676
- https://nvd.nist.gov/vuln/detail/CVE-2021-22184
