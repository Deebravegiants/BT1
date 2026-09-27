# [H] Deserialization of Untrusted Data in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2026-1184
Aliases: CVE-2026-1184
Ecosystem: Bitnami
Published: 2026-05-18
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-1184
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.11.0 <18.11.3

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 11.9 before 18.9.7, 18.10 before 18.10.6, and 18.11 before 18.11.3 that could have allowed an unauthenticated user to cause denial of service by uploading a specially crafted file due to improper validation.

## References
- https://about.gitlab.com/releases/2026/05/13/patch-release-gitlab-18-11-3-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/586634
- https://hackerone.com/reports/3515842
- https://nvd.nist.gov/vuln/detail/CVE-2026-1184
