# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-6171
Aliases: CVE-2025-6171
Ecosystem: Bitnami
Published: 2025-11-21
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-6171
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.5.0 <18.5.2

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 13.2 before 18.3.6, 18.4 before 18.4.4, and 18.5 before 18.5.2 that could have allowed an authenticated attacker with reporter access to view branch names and pipeline details by accessing the packages API endpoint even when repository access was disabled.

## References
- https://about.gitlab.com/releases/2025/11/12/patch-release-gitlab-18-5-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/549730
- https://hackerone.com/reports/3183740
- https://nvd.nist.gov/vuln/detail/CVE-2025-6171
