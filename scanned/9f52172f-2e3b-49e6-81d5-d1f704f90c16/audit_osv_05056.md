# [M] BIT-gitlab-2021-22221

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-22221
Aliases: CVE-2021-22221
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22221
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.12.0 <13.12.2

## Details
An issue has been discovered in GitLab affecting all versions starting from 12.9.0 before 13.10.5, all versions starting from 13.11.0 before 13.11.5, all versions starting from 13.12.0 before 13.12.2. Insufficient expired password validation in various operations allow user to maintain limited access after their password expired

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22221.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/292006
- https://nvd.nist.gov/vuln/detail/CVE-2021-22221
