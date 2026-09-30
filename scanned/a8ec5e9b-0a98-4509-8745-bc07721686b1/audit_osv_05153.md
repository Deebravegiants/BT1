# [H] BIT-gitlab-2021-39944

## Summary
Severity: High
Advisory: BIT-gitlab-2021-39944
Aliases: CVE-2021-39944
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39944
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.5.0 <14.5.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 11.0 before 14.3.6, all versions starting from 14.4 before 14.4.4, all versions starting from 14.5 before 14.5.2. A permissions validation flaw allowed group members with a developer role to elevate their privilege to a maintainer on projects they import

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39944.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/336531
- https://hackerone.com/reports/1256017
- https://nvd.nist.gov/vuln/detail/CVE-2021-39944
