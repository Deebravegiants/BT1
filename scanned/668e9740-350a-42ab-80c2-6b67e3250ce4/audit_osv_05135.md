# [M] BIT-gitlab-2021-39917

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39917
Aliases: CVE-2021-39917
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39917
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.5.0 <14.5.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 12.9 before 14.3.6, all versions starting from 14.4 before 14.4.4, all versions starting from 14.5 before 14.5.2. A regular expression related to quick actions features was susceptible to catastrophic backtracking that could cause a DOS attack.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39917.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/338486
- https://hackerone.com/reports/1277918
- https://nvd.nist.gov/vuln/detail/CVE-2021-39917
