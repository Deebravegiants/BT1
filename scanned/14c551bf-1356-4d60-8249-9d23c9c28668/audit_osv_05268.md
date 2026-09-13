# [M] BIT-gitlab-2022-3067

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-3067
Aliases: CVE-2022-3067
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3067
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.4.0 <15.4.1

## Details
An issue has been discovered in the Import functionality of GitLab CE/EE affecting all versions starting from 14.4 before 15.2.5, all versions starting from 15.3 before 15.3.4, all versions starting from 15.4 before 15.4.1. It was possible for an authenticated user to read arbitrary projects' content given the project's ID.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3067.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/372165
- https://hackerone.com/reports/1685822
- https://nvd.nist.gov/vuln/detail/CVE-2022-3067
