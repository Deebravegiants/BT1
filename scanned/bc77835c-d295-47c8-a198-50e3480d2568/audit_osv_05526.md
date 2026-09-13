# [H] Missing Authorization in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2026-16494
Aliases: CVE-2026-16494
Ecosystem: Bitnami
Published: 2026-08-18
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-16494
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.2.0 <19.2.2

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 19.1 before 19.1.4 and 19.2 before 19.2.2 that under certain conditions could have allowed an authenticated user to modify project settings restricted to higher-privileged roles, due to missing authorization checks on a project update endpoint.

## References
- https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-2-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/606580
- https://hackerone.com/reports/3775445
- https://nvd.nist.gov/vuln/detail/CVE-2026-16494
