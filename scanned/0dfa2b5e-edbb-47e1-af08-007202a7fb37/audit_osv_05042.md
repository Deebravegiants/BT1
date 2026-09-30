# [C] BIT-gitlab-2021-22203

## Summary
Severity: Critical
Advisory: BIT-gitlab-2021-22203
Aliases: CVE-2021-22203
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22203
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.10.0 <13.10.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 13.7.9 before 13.8.7, all versions starting from 13.9 before 13.9.5, and all versions starting from 13.10 before 13.10.1. A specially crafted Wiki page allowed attackers to read arbitrary files on the server.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22203.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/320919
- https://hackerone.com/reports/1098793
- https://nvd.nist.gov/vuln/detail/CVE-2021-22203
