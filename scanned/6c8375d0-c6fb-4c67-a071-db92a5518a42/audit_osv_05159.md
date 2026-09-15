# [M] BIT-gitlab-2022-0124

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-0124
Aliases: CVE-2022-0124
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0124
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.6.0 <14.6.1

## Details
An issue has been discovered affecting GitLab versions prior to 14.4.5, between 14.5.0 and 14.5.3, and between 14.6.0 and 14.6.1. Gitlab's Slack integration is incorrectly validating user input and allows to craft malicious URLs that are sent to slack.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0124.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/340176
- https://hackerone.com/reports/1310778
- https://nvd.nist.gov/vuln/detail/CVE-2022-0124
