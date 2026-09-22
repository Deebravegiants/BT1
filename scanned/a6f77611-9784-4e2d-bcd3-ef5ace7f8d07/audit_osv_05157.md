# [M] BIT-gitlab-2022-0093

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-0093
Aliases: CVE-2022-0093
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0093
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.6.0 <14.6.1

## Details
An issue has been discovered affecting GitLab versions prior to 14.4.5, between 14.5.0 and 14.5.3, and between 14.6.0 and 14.6.1. GitLab allows a user with an expired password to access sensitive information through RSS feeds.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0093.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/343247
- https://hackerone.com/reports/1348738
- https://nvd.nist.gov/vuln/detail/CVE-2022-0093
