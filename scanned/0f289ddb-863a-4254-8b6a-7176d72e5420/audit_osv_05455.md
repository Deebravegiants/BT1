# [M] Incomplete Comparison with Missing Factors in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-5528
Aliases: CVE-2024-5528
Ecosystem: Bitnami
Published: 2025-02-07
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-5528
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=0 <17.1.2

## Details
An issue was discovered in GitLab CE/EE affecting all versions prior to 16.11.6, starting from 17.0 prior to 17.0.4, and starting from 17.1 prior to 17.1.2, which allows a subdomain takeover in GitLab Pages.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/464558
- https://hackerone.com/reports/2523654
- https://about.gitlab.com/releases/2024/07/10/patch-release-gitlab-17-1-2-released/
- https://nvd.nist.gov/vuln/detail/CVE-2024-5528
