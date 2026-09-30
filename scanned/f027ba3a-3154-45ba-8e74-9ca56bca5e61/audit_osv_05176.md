# [M] BIT-gitlab-2022-0477

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-0477
Aliases: CVE-2022-0477
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0477
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.7.0 <14.7.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 11.9 before 14.5.4, all versions starting from 14.6.0 before 14.6.4, all versions starting from 14.7.0 before 14.7.1. GitLab was not correctly handling bulk requests to delete existing packages from the package registries which could result in a Denial of Service under specific conditions.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0477.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/348166
- https://nvd.nist.gov/vuln/detail/CVE-2022-0477
