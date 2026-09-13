# [H] Missing Authorization in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2025-11989
Aliases: CVE-2025-11989
Ecosystem: Bitnami
Published: 2025-10-28
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-11989
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.5.0 <18.5.1

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 17.6.0 before 18.3.5, 18.4 before 18.4.3, and 18.5 before 18.5.1 that could have allowed an authenticated attacker to execute unauthorized quick actions by including malicious commands in specific descriptions.

## References
- https://about.gitlab.com/releases/2025/10/22/patch-release-gitlab-18-5-1-released/
- https://gitlab.com/gitlab-org/security/gitlab/-/issues/1426
- https://nvd.nist.gov/vuln/detail/CVE-2025-11989
