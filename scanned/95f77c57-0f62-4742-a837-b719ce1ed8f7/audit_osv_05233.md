# [M] BIT-gitlab-2022-2270

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-2270
Aliases: CVE-2022-2270
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2270
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.1.0 <15.1.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 12.4 before 14.10.5, all versions starting from 15.0 before 15.0.4, all versions starting from 15.1 before 15.1.1. GitLab was leaking Conan packages names due to incorrect permissions verification.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2270.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/223074
- https://hackerone.com/reports/901473
- https://nvd.nist.gov/vuln/detail/CVE-2022-2270
