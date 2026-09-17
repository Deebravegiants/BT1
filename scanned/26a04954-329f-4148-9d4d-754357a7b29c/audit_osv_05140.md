# [M] BIT-gitlab-2021-39931

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39931
Aliases: CVE-2021-39931
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39931
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.5.0 <14.5.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 8.11 before 14.3.6, all versions starting from 14.4 before 14.4.4, all versions starting from 14.5 before 14.5.2. Under specific condition an unauthorised project member was allowed to delete a protected branches due to a business logic error.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39931.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/340445
- https://hackerone.com/reports/1318379
- https://nvd.nist.gov/vuln/detail/CVE-2021-39931
