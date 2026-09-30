# [M] BIT-gitlab-2022-1188

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-1188
Aliases: CVE-2022-1188
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1188
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.9.0 <14.9.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 12.1 before 14.7.7, all versions starting from 14.8 before 14.8.5, all versions starting from 14.9 before 14.9.2 where a blind SSRF attack through the repository mirroring feature was possible.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1188.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/354059
- https://hackerone.com/reports/1486659
- https://nvd.nist.gov/vuln/detail/CVE-2022-1188
