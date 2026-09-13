# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-11971
Aliases: CVE-2025-11971
Ecosystem: Bitnami
Published: 2025-10-28
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-11971
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.5.0 <18.5.1

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 10.6 before 18.3.5, 18.4 before 18.4.3, and 18.5 before 18.5.1 that could have allowed an authenticated attacker to trigger unauthorized pipeline executions by manipulating commits.

## References
- https://about.gitlab.com/releases/2025/10/22/patch-release-gitlab-18-5-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/566587
- https://nvd.nist.gov/vuln/detail/CVE-2025-11971
