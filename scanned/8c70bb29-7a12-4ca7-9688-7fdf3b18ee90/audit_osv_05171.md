# [M] BIT-gitlab-2022-0371

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-0371
Aliases: CVE-2022-0371
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0371
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.7.0 <14.7.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 11.4 before 14.5.4, all versions starting from 14.6 before 14.6.4, all versions starting from 14.7 before 14.7.1. GitLab search may allow authenticated users to search other users by their respective private emails even if a user set their email to private.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0371.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/350476
- https://nvd.nist.gov/vuln/detail/CVE-2022-0371
