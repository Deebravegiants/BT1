# [M] BIT-gitlab-2021-22257

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-22257
Aliases: CVE-2021-22257
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22257
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.2.0 <14.2.2

## Details
An issue has been discovered in GitLab affecting all versions starting from 14.0 before 14.0.9, all versions starting from 14.1 before 14.1.4, all versions starting from 14.2 before 14.2.2. The route for /user.keys is not restricted on instances with public visibility disabled. This allows user enumeration on such instances.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22257.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/23832
- https://nvd.nist.gov/vuln/detail/CVE-2021-22257
