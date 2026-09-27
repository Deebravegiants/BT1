# [M] BIT-gitlab-2022-1963

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-1963
Aliases: CVE-2022-1963
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1963
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.1.0 <15.1.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 13.4 before 14.10.5, all versions starting from 15.0 before 15.0.4, all versions starting from 15.1 before 15.1.1. GitLab reveals if a user has enabled two-factor authentication on their account in the HTML source, to unauthenticated users.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1963.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/352210
- https://hackerone.com/reports/1470023
- https://nvd.nist.gov/vuln/detail/CVE-2022-1963
