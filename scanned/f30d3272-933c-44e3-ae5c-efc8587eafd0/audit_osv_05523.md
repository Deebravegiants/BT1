# [M] Acceptance of Extraneous Untrusted Data With Trusted Data in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-15387
Aliases: CVE-2026-15387
Ecosystem: Bitnami
Published: 2026-09-01
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-15387
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.3.0 <19.3.1

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 19.1 before 19.1.7, 19.2 before 19.2.5, and 19.3 before 19.3.1 that, under certain conditions, an authenticated user with developer-role permissions could have influenced the execution environment of Pipeline Execution Policy enforcement jobs, due to improper handling of job dependencies.

## References
- https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-3-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/605632
- https://hackerone.com/reports/3754358
- https://nvd.nist.gov/vuln/detail/CVE-2026-15387
