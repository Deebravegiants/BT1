# [M] BIT-gitlab-2023-1621

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-1621
Aliases: CVE-2023-1621
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-1621
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.11.0 <15.11.1

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 12.0 before 15.10.5, all versions starting from 15.11 before 15.11.1. A malicious group member may continue to commit to projects even from a restricted IP address.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-1621.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/399774
- https://hackerone.com/reports/1914049
- https://nvd.nist.gov/vuln/detail/CVE-2023-1621
