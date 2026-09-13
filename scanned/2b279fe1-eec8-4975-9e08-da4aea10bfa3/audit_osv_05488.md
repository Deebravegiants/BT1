# [M] Memory Allocation with Excessive Size Value in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-12983
Aliases: CVE-2025-12983
Ecosystem: Bitnami
Published: 2025-11-20
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-12983
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.5.0 <18.5.2

## Details
GitLab has remediated an issue in GitLab CE/EE affecting all versions from 16.9 before 18.3.6, 18.4 before 18.4.4, and 18.5 before 18.5.2 that could have allowed an authenticated attacker to cause a denial of service condition by submitting specially crafted markdown content with nested formatting patterns.

## References
- https://about.gitlab.com/releases/2025/11/12/patch-release-gitlab-18-5-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/296257
- https://hackerone.com/reports/3419588
- https://nvd.nist.gov/vuln/detail/CVE-2025-12983
