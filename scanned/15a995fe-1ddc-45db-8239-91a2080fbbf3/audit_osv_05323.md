# [M] BIT-gitlab-2022-4365

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-4365
Aliases: CVE-2022-4365
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-4365
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.7.0 <15.7.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 11.8 before 15.5.7, all versions starting from 15.6 before 15.6.4, all versions starting from 15.7 before 15.7.2. A malicious Maintainer can leak the sentry token by changing the configured URL in the Sentry error tracking settings page.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-4365.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/385193
- https://hackerone.com/reports/1792626
- https://nvd.nist.gov/vuln/detail/CVE-2022-4365
