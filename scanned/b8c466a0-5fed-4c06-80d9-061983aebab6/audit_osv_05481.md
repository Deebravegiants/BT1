# [H] Missing Authorization in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2025-11702
Aliases: CVE-2025-11702
Ecosystem: Bitnami
Published: 2025-11-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-11702
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.5.0 <18.5.1

## Details
GitLab has remediated an issue in EE affecting all versions from 17.1 before 18.3.5, 18.4 before 18.4.3, and 18.5 before 18.5.1 that could have allowed an authenticated attacker with specific permissions to hijack project runners from other projects.

## References
- https://about.gitlab.com/releases/2025/10/22/patch-release-gitlab-18-5-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/576900
- https://hackerone.com/reports/3356284
- https://nvd.nist.gov/vuln/detail/CVE-2025-11702
