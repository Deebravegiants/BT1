# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-6840
Aliases: CVE-2023-6840
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-6840
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.8.0 <16.8.2

## Details
An issue has been discovered in GitLab EE affecting all versions from 16.4 prior to 16.6.7, 16.7 prior to 16.7.5, and 16.8 prior to 16.8.2 which allows a maintainer to change the name of a protected branch that bypasses the security policy added to block MR.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/435500
- https://hackerone.com/reports/2280292
- https://nvd.nist.gov/vuln/detail/CVE-2023-6840
