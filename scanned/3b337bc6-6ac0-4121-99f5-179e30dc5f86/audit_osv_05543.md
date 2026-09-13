# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-5377
Aliases: CVE-2026-5377
Ecosystem: Bitnami
Published: 2026-04-24
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-5377
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.11.0 <18.11.1

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 18.11 before 18.11.1 that could have allowed an authenticated user to access titles of confidential or private issues in public projects due to improper access control in the issue description rendering process.

## References
- https://about.gitlab.com/releases/2026/04/22/patch-release-gitlab-18-11-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/595553
- https://hackerone.com/reports/3640688
- https://nvd.nist.gov/vuln/detail/CVE-2026-5377
