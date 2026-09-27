# [M] BIT-gitlab-2022-3758

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-3758
Aliases: CVE-2022-3758
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3758
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.9.0 <15.9.2

## Details
An issue has been discovered in GitLab affecting all versions starting from 15.5 before 15.7.8, all versions starting from 15.8 before 15.8.4, all versions starting from 15.9 before 15.9.2. Due to improper permissions checks an unauthorised user was able to read, add or edit a users private snippet.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3758.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/379598
- https://hackerone.com/reports/1751258
- https://nvd.nist.gov/vuln/detail/CVE-2022-3758
