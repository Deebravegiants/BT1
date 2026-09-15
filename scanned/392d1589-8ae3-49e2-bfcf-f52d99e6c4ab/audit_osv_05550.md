# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-6713
Aliases: CVE-2026-6713
Ecosystem: Bitnami
Published: 2026-05-28
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-6713
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.0.0 <19.0.2

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 18.2 before 18.10.7, 18.11 before 18.11.4, and 19.0 before 19.0.1 that under certain conditions could have allowed an unauthorized user to enumerate private projects due to incorrect authorization checks.

## References
- https://about.gitlab.com/releases/2026/05/27/patch-release-gitlab-19-0-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/597490
- https://hackerone.com/reports/3644605
- https://nvd.nist.gov/vuln/detail/CVE-2026-6713
