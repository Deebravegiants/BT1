# [H] Time-of-check Time-of-use (TOCTOU) Race Condition in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2024-9183
Aliases: CVE-2024-9183
Ecosystem: Bitnami
Published: 2025-12-09
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-9183
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.6.0 <18.6.1

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 18.4 prior to 18.4.5, 18.5 prior to 18.5.3, and 18.6 prior to 18.6.1 that could have allowed an authenticated user to obtain credentials from higher-privileged users and perform actions in their context under specific conditions.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/494478
- https://hackerone.com/reports/2707421
- https://nvd.nist.gov/vuln/detail/CVE-2024-9183
- https://about.gitlab.com/releases/2025/11/26/patch-release-gitlab-18-6-1-released/
