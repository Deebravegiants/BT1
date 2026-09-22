# [M] BIT-gitlab-2021-4191

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-4191
Aliases: CVE-2021-4191
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-4191
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.8.0 <14.8.2

## Details
An issue has been discovered in GitLab CE/EE affecting versions 13.0 to 14.6.5, 14.7 to 14.7.4, and 14.8 to 14.8.2. Private GitLab instances with restricted sign-ups may be vulnerable to user enumeration to unauthenticated users through the GraphQL API.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-4191.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/343898
- https://hackerone.com/reports/1089609
- https://nvd.nist.gov/vuln/detail/CVE-2021-4191
