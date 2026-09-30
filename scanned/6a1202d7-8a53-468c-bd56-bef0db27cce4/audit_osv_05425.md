# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-10219
Aliases: CVE-2024-10219
Ecosystem: Bitnami
Published: 2025-08-18
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-10219
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.2.0 <18.2.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions from 15.6 before 18.0.6, 18.1 before 18.1.4, and 18.2 before 18.2.2 that under certain conditions could have allowed authenticated users to bypass access controls and download private artifacts by accessing specific API endpoints.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/500134
- https://hackerone.com/reports/2780353
- https://nvd.nist.gov/vuln/detail/CVE-2024-10219
