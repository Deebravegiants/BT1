# [H] Improper Handling of Parameters in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2026-2370
Aliases: CVE-2026-2370
Ecosystem: Bitnami
Published: 2026-03-31
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-2370
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.10.0 <18.10.1

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 14.3 before 18.8.7, 18.9 before 18.9.3, and 18.10 before 18.10.1 affecting Jira Connect installations that could have allowed an authenticated user with minimal workspace permissions to obtain installation credentials and impersonate the GitLab app due to improper authorization checks.

## References
- https://about.gitlab.com/releases/2026/03/25/patch-release-gitlab-18-10-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/589635
- https://hackerone.com/reports/3522829
- https://nvd.nist.gov/vuln/detail/CVE-2026-2370
- https://access.redhat.com/security/cve/CVE-2026-2370
- https://bugzilla.redhat.com/show_bug.cgi?id=2452920
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-2370.json
