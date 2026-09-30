# [M] Improper Removal of Sensitive Information Before Storage or Transfer in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-1182
Aliases: CVE-2026-1182
Ecosystem: Bitnami
Published: 2026-03-14
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-1182
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.9.0 <18.9.2

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 8.14 before 18.7.6, 18.8 before 18.8.6, and 18.9 before 18.9.2 that could have allowed an authenticated user to gain unauthorized access to confidential issue title created in public projects under certain circumstances.

## References
- https://gitlab.com/gitlab-org/gitlab/-/work_items/586613
- https://hackerone.com/reports/3515716
- https://nvd.nist.gov/vuln/detail/CVE-2026-1182
