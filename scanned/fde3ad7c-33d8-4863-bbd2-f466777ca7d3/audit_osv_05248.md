# [M] BIT-gitlab-2022-2531

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-2531
Aliases: CVE-2022-2531
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2531
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.2.0 <15.2.1

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 12.5 before 15.0.5, all versions starting from 15.1 before 15.1.4, all versions starting from 15.2 before 15.2.1. GitLab was not performing correct authentication on Grafana API under specific conditions allowing unauthenticated users to perform queries through a path traversal vulnerability.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2531.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/364252
- https://hackerone.com/reports/1566306
- https://nvd.nist.gov/vuln/detail/CVE-2022-2531
