# [M] BIT-gitlab-2022-4342

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-4342
Aliases: CVE-2022-4342
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-4342
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.7.0 <15.7.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 15.1 before 15.5.7, all versions starting from 15.6 before 15.6.4, all versions starting from 15.7 before 15.7.2. A malicious Maintainer can leak masked webhook secrets by changing target URL of the webhook.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-4342.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/385118
- https://hackerone.com/reports/1791331
- https://nvd.nist.gov/vuln/detail/CVE-2022-4342
