# [M] Improper Neutralization of Substitution Characters in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-9694
Aliases: CVE-2026-9694
Ecosystem: Bitnami
Published: 2026-06-12
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-9694
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.0.0 <19.0.2

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 15.9 before 18.10.8, 18.11 before 18.11.5, and 19.0 before 19.0.2 that under certain conditions, could have allowed an unauthenticated user to impersonate the GitLab Support Bot and inject arbitrary content via a specially crafted Service Desk email reply due to improper neutralization in email template processing.

## References
- https://about.gitlab.com/releases/2026/06/10/patch-release-gitlab-19-0-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/601330
- https://hackerone.com/reports/3685720
- https://nvd.nist.gov/vuln/detail/CVE-2026-9694
