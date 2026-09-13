# [M] BIT-gitlab-2023-0319

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-0319
Aliases: CVE-2023-0319
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-0319
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.10.0 <15.10.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 13.6 before 15.8.5, all versions starting from 15.9 before 15.9.4, all versions starting from 15.10 before 15.10.1, allowing to read environment names supposed to be restricted to project memebers only.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-0319.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/388096
- https://hackerone.com/reports/1817586
- https://nvd.nist.gov/vuln/detail/CVE-2023-0319
