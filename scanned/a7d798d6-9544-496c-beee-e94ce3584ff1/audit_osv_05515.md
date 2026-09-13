# [M] Improper Validation of Unsafe Equivalence in Input in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-1094
Aliases: CVE-2026-1094
Ecosystem: Bitnami
Published: 2026-02-16
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-1094
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.8.0 <18.8.4

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 18.8 before 18.8.4 that could have allowed an authenticated developer to hide specially crafted file changes from the WebUI.

## References
- https://about.gitlab.com/releases/2026/02/10/patch-release-gitlab-18-8-4-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/586483
- https://hackerone.com/reports/3502519
- https://nvd.nist.gov/vuln/detail/CVE-2026-1094
