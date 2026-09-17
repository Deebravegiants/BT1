# [M] BIT-gitlab-2022-2512

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-2512
Aliases: CVE-2022-2512
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2512
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.2.0 <15.2.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 15.0 before 15.0.5, all versions starting from 15.1 before 15.1.4, all versions starting from 15.2 before 15.2.1. Membership changes are not reflected in TODO for confidential notes, allowing a former project members to read updates via TODOs.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2512.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/365742
- https://nvd.nist.gov/vuln/detail/CVE-2022-2512
