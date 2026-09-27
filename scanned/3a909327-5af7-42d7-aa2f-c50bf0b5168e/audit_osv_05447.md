# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-3976
Aliases: CVE-2024-3976
Ecosystem: Bitnami
Published: 2025-02-07
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-3976
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.0.0 <16.11.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 14.0 prior to 16.9.7, starting from 16.10 prior to 16.10.5, and starting from 16.11 prior to 16.11.2. It was possible to disclose via the UI the confidential issues title and description from a public project to unauthorised instance users.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/457140
- https://hackerone.com/reports/2470939
- https://about.gitlab.com/releases/2024/05/08/patch-release-gitlab-16-11-2-released/
- https://nvd.nist.gov/vuln/detail/CVE-2024-3976
