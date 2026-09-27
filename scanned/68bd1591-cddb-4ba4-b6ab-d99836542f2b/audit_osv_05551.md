# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-6821
Aliases: CVE-2026-6821
Ecosystem: Bitnami
Published: 2026-08-18
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-6821
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.2.0 <19.2.2

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 12.0 before 19.0.6, 19.1 before 19.1.4, and 19.2 before 19.2.2 that under certain conditions could have allowed an authenticated user to bypass IP-based access restrictions and read limited merge request information from a private project due to missing authorization checks in a merge requests API endpoint.

## References
- https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-2-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/597702
- https://hackerone.com/reports/3674254
- https://nvd.nist.gov/vuln/detail/CVE-2026-6821
