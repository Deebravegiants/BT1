# [M] BIT-gitlab-2023-2069

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-2069
Aliases: CVE-2023-2069
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-2069
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.0.0 <13.0.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 10.0 before 12.9.8, all versions starting from 12.10 before 12.10.7, all versions starting from 13.0 before 13.0.1. A user with the role of developer could use the import project feature to leak CI/CD variables.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-2069.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/407374
- https://hackerone.com/reports/1939987
- https://nvd.nist.gov/vuln/detail/CVE-2023-2069
