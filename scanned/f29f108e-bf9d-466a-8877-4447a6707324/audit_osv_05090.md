# [M] BIT-gitlab-2021-22264

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-22264
Aliases: CVE-2021-22264
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22264
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.2.0 <14.2.2

## Details
An issue has been discovered in GitLab affecting all versions starting from 13.8 before 14.0.9, all versions starting from 14.1 before 14.1.4, all versions starting from 14.2 before 14.2.2. Under specialized conditions, an invited group member may continue to have access to a project even after the invited group, which the member was part of, is deleted.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22264.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/336073
- https://nvd.nist.gov/vuln/detail/CVE-2021-22264
