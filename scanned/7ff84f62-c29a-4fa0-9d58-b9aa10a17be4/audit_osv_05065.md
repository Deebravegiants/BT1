# [C] BIT-gitlab-2021-22234

## Summary
Severity: Critical
Advisory: BIT-gitlab-2021-22234
Aliases: CVE-2021-22234
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22234
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.0.0 <14.0.4

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 13.11 before 13.11.7, all versions starting from 13.12 before 13.12.8, and all versions starting from 14.0 before 14.0.4. A specially crafted design image allowed attackers to read arbitrary files on the server.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22234.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/335205
- https://hackerone.com/reports/1212067
- https://nvd.nist.gov/vuln/detail/CVE-2021-22234
