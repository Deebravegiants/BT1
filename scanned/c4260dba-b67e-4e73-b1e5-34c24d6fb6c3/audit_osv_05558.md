# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-9807
Aliases: CVE-2026-9807
Ecosystem: Bitnami
Published: 2026-06-01
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-9807
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.0.0 <19.0.1

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 18.9 before 18.10.7, 18.11 before 18.11.4, and 19.0 before 19.0.1 that under certain conditions could have allowed a blocked Project Access Token to continue accessing private resources due to incorrect authorization enforcement.

## References
- https://about.gitlab.com/releases/2026/05/27/patch-release-gitlab-19-0-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/590694
- https://hackerone.com/reports/3554993
- https://nvd.nist.gov/vuln/detail/CVE-2026-9807
