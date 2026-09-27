# [M] BIT-gitlab-2022-3478

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-3478
Aliases: CVE-2022-3478
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3478
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.6.0 <15.6.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 12.8 before 15.4.6, all versions starting from 15.5 before 15.5.5, all versions starting from 15.6 before 15.6.1. It was possible to trigger a DoS attack by uploading a malicious nuget package.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3478.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/377788
- https://hackerone.com/reports/1716296
- https://nvd.nist.gov/vuln/detail/CVE-2022-3478
