# [M] BIT-gitlab-2021-22197

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-22197
Aliases: CVE-2021-22197
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22197
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.10.0 <13.10.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 10.6 where an infinite loop exist when an authenticated user with specific rights access a MR having source and target branch pointing to each other

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22197.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/323198
- https://nvd.nist.gov/vuln/detail/CVE-2021-22197
