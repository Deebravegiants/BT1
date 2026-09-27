# [M] BIT-gitlab-2022-2303

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-2303
Aliases: CVE-2022-2303
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2303
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.2.0 <15.2.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions before 15.0.5, all versions starting from 15.1 before 15.1.4, all versions starting from 15.2 before 15.2.1. It may be possible for group members to bypass 2FA enforcement enabled at the group level by using Resource Owner Password Credentials grant to obtain an access token without using 2FA.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2303.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/355028
- https://hackerone.com/reports/1498133
- https://nvd.nist.gov/vuln/detail/CVE-2022-2303
