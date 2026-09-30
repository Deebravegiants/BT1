# [H] Improper Resolution of Path Equivalence in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2026-5816
Aliases: CVE-2026-5816
Ecosystem: Bitnami
Published: 2026-04-24
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-5816
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.11.0 <18.11.1

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 18.10 before 18.10.4 and 18.11 before 18.11.1 that could have allowed an unauthenticated user to execute arbitrary JavaScript in a user's browser session due to improper path validation under certain conditions.

## References
- https://about.gitlab.com/releases/2026/04/22/patch-release-gitlab-18-11-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/592816
- https://hackerone.com/reports/3572231
- https://nvd.nist.gov/vuln/detail/CVE-2026-5816
