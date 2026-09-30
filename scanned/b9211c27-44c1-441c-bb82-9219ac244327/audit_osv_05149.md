# [M] BIT-gitlab-2021-39940

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39940
Aliases: CVE-2021-39940
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39940
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.5.0 <14.5.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 13.2 before 14.3.6, all versions starting from 14.4 before 14.4.4, all versions starting from 14.5 before 14.5.2. GitLab Maven Package registry is vulnerable to a regular expression denial of service when a specifically crafted string is sent.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39940.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/263116
- https://hackerone.com/reports/997961
- https://nvd.nist.gov/vuln/detail/CVE-2021-39940
