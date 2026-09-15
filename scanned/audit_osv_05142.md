# [M] BIT-gitlab-2021-39933

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39933
Aliases: CVE-2021-39933
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39933
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.5.0 <14.5.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 12.10 before 14.3.6, all versions starting from 14.4 before 14.4.4, all versions starting from 14.5 before 14.5.2. A regular expression used for handling user input (notes, comments, etc) was susceptible to catastrophic backtracking that could cause a DOS attack.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39933.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/340449
- https://hackerone.com/reports/1320077
- https://nvd.nist.gov/vuln/detail/CVE-2021-39933
