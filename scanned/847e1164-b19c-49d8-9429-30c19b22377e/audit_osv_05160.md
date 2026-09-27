# [M] BIT-gitlab-2022-0125

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-0125
Aliases: CVE-2022-0125
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0125
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.6.0 <14.6.2

## Details
An issue has been discovered in GitLab affecting all versions starting from 12.0 before 14.4.5, all versions starting from 14.5.0 before 14.5.3, all versions starting from 14.6.0 before 14.6.2. GitLab was not verifying that a maintainer of a project had the right access to import members from a target project.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0125.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/345564
- https://hackerone.com/reports/1356100
- https://nvd.nist.gov/vuln/detail/CVE-2022-0125
