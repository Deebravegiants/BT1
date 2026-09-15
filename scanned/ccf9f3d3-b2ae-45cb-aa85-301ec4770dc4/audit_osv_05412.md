# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-5612
Aliases: CVE-2023-5612
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-5612
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.8.0 <16.8.1

## Details
An issue has been discovered in GitLab affecting all versions before 16.6.6, 16.7 prior to 16.7.4, and 16.8 prior to 16.8.1. It was possible to read the user email address via tags feed although the visibility in the user profile has been disabled.

## References
- https://about.gitlab.com/releases/2024/01/25/critical-security-release-gitlab-16-8-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/428441
- https://hackerone.com/reports/2208790
- https://nvd.nist.gov/vuln/detail/CVE-2023-5612
