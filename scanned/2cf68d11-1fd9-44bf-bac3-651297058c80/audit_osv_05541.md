# [H] Exposed Dangerous Method or Function in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2026-5173
Aliases: CVE-2026-5173
Ecosystem: Bitnami
Published: 2026-04-17
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-5173
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.10.0 <18.10.3

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 16.9.6 before 18.8.9, 18.9 before 18.9.5, and 18.10 before 18.10.3 that could have allowed an authenticated user to invoke unintended server-side methods through websocket connections due to improper access control.

## References
- https://about.gitlab.com/releases/2026/04/08/patch-release-gitlab-18-10-3-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/588959
- https://nvd.nist.gov/vuln/detail/CVE-2026-5173
