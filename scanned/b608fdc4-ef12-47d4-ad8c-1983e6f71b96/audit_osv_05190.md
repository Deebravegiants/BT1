# [M] BIT-gitlab-2022-1124

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-1124
Aliases: CVE-2022-1124
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1124
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.10.0 <14.10.1

## Details
An improper authorization issue has been discovered in GitLab CE/EE affecting all versions prior to 14.8.6, all versions from 14.9.0 prior to 14.9.4, and 14.10.0, allowing Guest project members to access trace log of jobs when it is enabled

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1124.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/323552
- https://hackerone.com/reports/1113405
- https://nvd.nist.gov/vuln/detail/CVE-2022-1124
