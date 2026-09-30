# [M] Direct Request ('Forced Browsing') in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-6195
Aliases: CVE-2025-6195
Ecosystem: Bitnami
Published: 2025-12-02
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-6195
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.6.0 <18.6.1

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 13.7 before 18.4.5, 18.5 before 18.5.3, and 18.6 before 18.6.1 that could have allowed an authenticated user to view information from security reports under certain configuration conditions.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/549937
- https://hackerone.com/reports/3155693
- https://nvd.nist.gov/vuln/detail/CVE-2025-6195
- https://about.gitlab.com/releases/2025/11/26/patch-release-gitlab-18-6-1-released/
