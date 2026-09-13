# [H] Incorrect Authorization in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2025-11340
Aliases: CVE-2025-11340
Ecosystem: Bitnami
Published: 2025-10-11
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-11340
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.4.0 <18.4.2

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 18.3 to 18.3.4, 18.4 to 18.4.2 that, under certain conditions, could have allowed authenticated users with read-only API tokens to perform unauthorized write operations on vulnerability records by exploiting incorrectly scoped GraphQL mutations.

## References
- https://about.gitlab.com/releases/2025/10/08/patch-release-gitlab-18-4-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/567847
- https://nvd.nist.gov/vuln/detail/CVE-2025-11340
