# [M] BIT-gitlab-2023-0838

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-0838
Aliases: CVE-2023-0838
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-0838
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.10.0 <15.10.1

## Details
An issue has been discovered in GitLab affecting versions starting from 15.1 before 15.8.5, 15.9 before 15.9.4, and 15.10 before 15.10.1. A maintainer could modify a webhook URL to leak masked webhook secrets by adding a new parameter to the url. This addresses an incomplete fix for CVE-2022-4342.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-0838.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/391685
- https://hackerone.com/reports/1871136
- https://nvd.nist.gov/vuln/detail/CVE-2023-0838
