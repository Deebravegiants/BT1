# [M] BIT-gitlab-2022-0151

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-0151
Aliases: CVE-2022-0151
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0151
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.6.0 <14.6.2

## Details
An issue has been discovered in GitLab affecting all versions starting from 12.10 before 14.4.5, all versions starting from 14.5.0 before 14.5.3, all versions starting from 14.6.0 before 14.6.2. GitLab was not correctly handling requests to delete existing packages which could result in a Denial of Service under specific conditions.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0151.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/348176
- https://nvd.nist.gov/vuln/detail/CVE-2022-0151
