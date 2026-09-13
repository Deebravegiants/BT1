# [M] BIT-gitlab-2022-4289

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-4289
Aliases: CVE-2022-4289
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-4289
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.9.0 <15.9.2

## Details
An issue has been discovered in GitLab affecting all versions starting from 15.3 before 15.7.8, versions of 15.8 before 15.8.4, and version 15.9 before 15.9.2. Google IAP details in Prometheus integration were not hidden, could be leaked from instance, group, or project settings to other users.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-4289.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/384580
- https://hackerone.com/reports/1780770
- https://security.netapp.com/advisory/ntap-20240415-0004/
- https://nvd.nist.gov/vuln/detail/CVE-2022-4289
