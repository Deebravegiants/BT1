# [M] BIT-gitlab-2022-3018

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-3018
Aliases: CVE-2022-3018
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3018
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.4.0 <15.4.1

## Details
An information disclosure vulnerability in GitLab CE/EE affecting all versions starting from 9.3 before 15.2.5, all versions starting from 15.3 before 15.3.4, all versions starting from 15.4 before 15.4.1 allows a project maintainer to access the DataDog integration API key from webhook logs.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3018.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/360938
- https://nvd.nist.gov/vuln/detail/CVE-2022-3018
