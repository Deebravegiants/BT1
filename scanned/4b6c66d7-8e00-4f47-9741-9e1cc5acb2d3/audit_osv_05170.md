# [M] BIT-gitlab-2022-0344

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-0344
Aliases: CVE-2022-0344
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0344
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.7.0 <14.7.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 10.0 before 14.5.4, all versions starting from 10.1 before 14.6.4, all versions starting from 10.2 before 14.7.1. Private project paths can be disclosed to unauthorized users via system notes when an Issue is closed via a Merge Request and later moved to a public project

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0344.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/37015
- https://hackerone.com/reports/724880
- https://nvd.nist.gov/vuln/detail/CVE-2022-0344
