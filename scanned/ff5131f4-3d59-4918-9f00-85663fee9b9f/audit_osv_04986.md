# [M] BIT-gitlab-2020-13349

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-13349
Aliases: CVE-2020-13349
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13349
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=0 <13.5.2, >=13.5.0

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 8.12. A regular expression related to a file path resulted in the Advanced Search feature susceptible to catastrophic backtracking. Affected versions are >=8.12, <13.3.9,>=13.4, <13.4.5,>=13.5, <13.5.2.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13349.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/257497
