# [H] Interpretation Conflict in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2026-0958
Aliases: CVE-2026-0958
Ecosystem: Bitnami
Published: 2026-02-16
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-0958
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.8.0 <18.8.4

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 18.4 before 18.6.6, 18.7 before 18.7.4, and 18.8 before 18.8.4 that could have allowed an unauthenticated user to cause denial of service through memory or CPU exhaustion by bypassing JSON validation middleware limits.

## References
- https://about.gitlab.com/releases/2026/02/10/patch-release-gitlab-18-8-4-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/586202
- https://hackerone.com/reports/3463363
- https://nvd.nist.gov/vuln/detail/CVE-2026-0958
