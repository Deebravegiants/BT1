# [M] BIT-gitlab-2023-1265

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-1265
Aliases: CVE-2023-1265
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-1265
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.11.0 <15.11.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 11.9 before 15.9.6, all versions starting from 15.10 before 15.10.5, all versions starting from 15.11 before 15.11.1. The condition allows for a privileged attacker, under certain conditions, to obtain session tokens from all users of a GitLab instance.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-1265.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/394960
- https://hackerone.com/reports/1888690
- https://nvd.nist.gov/vuln/detail/CVE-2023-1265
