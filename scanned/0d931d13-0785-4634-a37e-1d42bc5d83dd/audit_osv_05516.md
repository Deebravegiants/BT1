# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-11379
Aliases: CVE-2026-11379
Ecosystem: Bitnami
Published: 2026-06-29
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-11379
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.1.0 <19.1.1

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 13.11 prior to 18.11.6, 19.0 prior to 19.0.3, and 19.1 prior to 19.1.1 in which incorrect authorization in DAST site profile management could allow a user with Developer role to exfiltrate DAST site profile secrets under certain conditions.

## References
- https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-1-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/517659
- https://nvd.nist.gov/vuln/detail/CVE-2026-11379
