# [M] Generation of Incorrect Security Tokens in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-15831
Aliases: CVE-2026-15831
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-15831
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.2.0 <19.2.1

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 19.1 before 19.1.3 and 19.2 before 19.2.1 that under certain conditions could have allowed an authenticated user to bypass administrator-configured tool governance policies due to improper authorization enforcement during token generation.

## References
- https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-2-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/605484
- https://nvd.nist.gov/vuln/detail/CVE-2026-15831
