# [H] Uncontrolled Recursion in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2026-1069
Aliases: CVE-2026-1069
Ecosystem: Bitnami
Published: 2026-03-13
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-1069
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.9.0 <18.9.2

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 18.9 before 18.9.2 that could have allowed an unauthenticated user to cause a denial of service by sending specially crafted GraphQL requests due to uncontrolled recursion under certain circumstances.

## References
- https://about.gitlab.com/releases/2026/03/11/patch-release-gitlab-18-9-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/586474
- https://hackerone.com/reports/3483687
- https://nvd.nist.gov/vuln/detail/CVE-2026-1069
