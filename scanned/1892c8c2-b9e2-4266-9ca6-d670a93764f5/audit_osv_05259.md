# [M] BIT-gitlab-2022-2907

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-2907
Aliases: CVE-2022-2907
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2907
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.3.0 <15.3.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 12.9 before 15.1.6, all versions starting from 15.2 before 15.2.4, all versions starting from 15.3 before 15.3.2. It was possible to read repository content by an unauthorised user if a project member used a crafted link.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2907.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/349388
- https://hackerone.com/reports/1417680
- https://nvd.nist.gov/vuln/detail/CVE-2022-2907
