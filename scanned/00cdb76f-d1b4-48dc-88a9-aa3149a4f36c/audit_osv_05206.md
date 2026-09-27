# [M] BIT-gitlab-2022-1428

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-1428
Aliases: CVE-2022-1428
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1428
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.10.0 <14.10.1

## Details
An issue has been discovered in GitLab affecting all versions before 14.8.6, all versions starting from 14.9 before 14.9.4, all versions starting from 14.10 before 14.10.1. GitLab was incorrectly verifying throttling limits for authenticated package requests which resulted in limits not being enforced.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1428.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/342481
- https://nvd.nist.gov/vuln/detail/CVE-2022-1428
