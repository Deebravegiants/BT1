# [M] BIT-gitlab-2022-3325

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-3325
Aliases: CVE-2022-3325
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3325
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.4.0 <15.4.1

## Details
Improper access control in the GitLab CE/EE API affecting all versions starting from 12.8 before 15.2.5, all versions starting from 15.3 before 15.3.4, all versions starting from 15.4 before 15.4.1. Allowed for editing the approval rules via the API by an unauthorised user.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3325.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/360819
- https://nvd.nist.gov/vuln/detail/CVE-2022-3325
