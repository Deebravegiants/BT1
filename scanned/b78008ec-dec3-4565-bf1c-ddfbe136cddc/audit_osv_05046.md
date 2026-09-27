# [H] BIT-gitlab-2021-22209

## Summary
Severity: High
Advisory: BIT-gitlab-2021-22209
Aliases: CVE-2021-22209
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22209
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.11.0 <13.11.12

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 13.8. GitLab was not properly validating authorisation tokens which resulted in GraphQL mutation being executed.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22209.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/327155
- https://nvd.nist.gov/vuln/detail/CVE-2021-22209
