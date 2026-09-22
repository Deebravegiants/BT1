# [M] BIT-gitlab-2023-1204

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-1204
Aliases: CVE-2023-1204
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-1204
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.0.0 <13.0.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 10.1 before 15.10.8, all versions starting from 15.11 before 15.11.7, all versions starting from 16.0 before 16.0.2. A user could use an unverified email as a public email and commit email by sending a specifically crafted request on user update settings.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-1204.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/394745
- https://hackerone.com/reports/1881598
- https://nvd.nist.gov/vuln/detail/CVE-2023-1204
