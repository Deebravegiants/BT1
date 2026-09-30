# [M] BIT-gitlab-2022-2534

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-2534
Aliases: CVE-2022-2534
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2534
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.2.0 <15.2.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 9.3 before 15.0.5, all versions starting from 15.1 before 15.1.4, all versions starting from 15.2 before 15.2.1. GitLab was returning contributor emails due to improper data handling in the Datadog integration.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2534.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/361654
- https://nvd.nist.gov/vuln/detail/CVE-2022-2534
