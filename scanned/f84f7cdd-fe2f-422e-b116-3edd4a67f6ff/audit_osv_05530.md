# [H] Inclusion of Functionality from Untrusted Control Sphere in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2026-18252
Aliases: CVE-2026-18252
Ecosystem: Bitnami
Published: 2026-09-01
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-18252
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.3.0 <19.3.1

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 18.9 before 19.1.7, 19.2 before 19.2.5, and 19.3 before 19.3.1 that, under certain conditions, an authenticated user with developer-role permissions could have executed arbitrary commands in a CI context, due to the Claude agent processing configuration from a user-controlled source.

## References
- https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-3-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/607342
- https://hackerone.com/reports/3863650
- https://nvd.nist.gov/vuln/detail/CVE-2026-18252
