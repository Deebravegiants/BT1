# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-12431
Aliases: CVE-2024-12431
Ecosystem: Bitnami
Published: 2025-01-10
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-12431
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.7.0 <17.7.1

## Details
An issue was discovered in GitLab CE/EE affecting all versions starting from 15.5 before 17.5.5, 17.6 before 17.6.3, and 17.7 before 17.7.1, in which unauthorized users could manipulate the status of issues in public projects.

## References
- https://about.gitlab.com/releases/2025/01/08/patch-release-gitlab-17-7-1-released/#unauthorized-user-can-manipulate-status-of-issues-in-public-projects
- https://gitlab.com/gitlab-org/gitlab/-/issues/508742
- https://hackerone.com/reports/2877710
- https://nvd.nist.gov/vuln/detail/CVE-2024-12431
