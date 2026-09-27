# [H] Unchecked Return Value in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2026-0723
Aliases: CVE-2026-0723
Ecosystem: Bitnami
Published: 2026-01-27
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-0723
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.8.0 <18.8.2

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 18.6 before 18.6.4, 18.7 before 18.7.2, and 18.8 before 18.8.2 that could have allowed an individual with existing knowledge of a victim's credential ID to bypass two-factor authentication by submitting forged device responses.

## References
- https://about.gitlab.com/releases/2026/01/21/patch-release-gitlab-18-8-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/585333
- https://hackerone.com/reports/3476052
- https://nvd.nist.gov/vuln/detail/CVE-2026-0723
