# [H] Missing Authorization in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2025-13772
Aliases: CVE-2025-13772
Ecosystem: Bitnami
Published: 2026-01-13
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-13772
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.7.0 <18.7.1

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 18.4 before 18.5.5, 18.6 before 18.6.3, and 18.7 before 18.7.1 that could have allowed an authenticated user to access and utilize AI model settings from unauthorized namespaces by manipulating namespace identifiers in API requests.

## References
- https://about.gitlab.com/releases/2026/01/07/patch-release-gitlab-18-7-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/581268
- https://nvd.nist.gov/vuln/detail/CVE-2025-13772
- https://access.redhat.com/security/cve/CVE-2025-13772
- https://bugzilla.redhat.com/show_bug.cgi?id=2428224
- https://security.access.redhat.com/data/csaf/v2/vex/2025/cve-2025-13772.json
