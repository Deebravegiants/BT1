# [M] Use of Incorrectly-Resolved Name or Reference in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-12506
Aliases: CVE-2025-12506
Ecosystem: Bitnami
Published: 2026-07-13
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-12506
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.1.0 <19.1.2

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 16.5 before 18.11.7, 19.0 before 19.0.4, and 19.1 before 19.1.2 that under certain conditions could have allowed an authenticated user to create a repository where the content displayed in the web interface differed from the content available for download, due to improper handling of Git reference name resolution.

## References
- https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-1-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/578988
- https://hackerone.com/reports/3351460
- https://nvd.nist.gov/vuln/detail/CVE-2025-12506
