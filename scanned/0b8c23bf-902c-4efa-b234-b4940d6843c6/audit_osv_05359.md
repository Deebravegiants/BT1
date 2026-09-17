# [M] BIT-gitlab-2023-1965

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-1965
Aliases: CVE-2023-1965
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-1965
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.11.0 <15.11.1

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 14.2 before 15.9.6, all versions starting from 15.10 before 15.10.5, all versions starting from 15.11 before 15.11.1. Lack of verification on RelayState parameter allowed a maliciously crafted URL to obtain access tokens granted for 3rd party Group SAML SSO logins. This feature isn't enabled by default.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-1965.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/406235
- https://hackerone.com/reports/1923672
- https://nvd.nist.gov/vuln/detail/CVE-2023-1965
