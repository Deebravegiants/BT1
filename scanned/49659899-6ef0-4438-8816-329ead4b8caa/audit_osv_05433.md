# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-12244
Aliases: CVE-2024-12244
Ecosystem: Bitnami
Published: 2025-04-26
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-12244
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.7.0 <17.11.1

## Details
An issue has been discovered in access controls could allow users to view certain restricted project information even when related features are disabled in GitLab EE, affecting all versions from 17.7 prior to 17.9.7, 17.10 prior to 17.10.5, and 17.11 prior to 17.11.1.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/508046
- https://hackerone.com/reports/2862754
- https://nvd.nist.gov/vuln/detail/CVE-2024-12244
