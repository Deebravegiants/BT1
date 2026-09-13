# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-1539
Aliases: CVE-2024-1539
Ecosystem: Bitnami
Published: 2025-02-07
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-1539
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.2.0 <16.11.2

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 15.2 prior to 16.9.7, starting from 16.10 prior to 16.10.5, and starting from 16.11 prior to 16.11.2. It was possible to disclose updates to issues to a banned group member using the API.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/442049
- https://hackerone.com/reports/2369988
- https://nvd.nist.gov/vuln/detail/CVE-2024-1539
