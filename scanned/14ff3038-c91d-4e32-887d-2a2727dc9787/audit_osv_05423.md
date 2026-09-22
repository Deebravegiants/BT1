# [M] Direct Request ('Forced Browsing') in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-0456
Aliases: CVE-2024-0456
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-0456
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.8.0 <16.8.1

## Details
An authorization vulnerability exists in GitLab versions 14.0 prior to 16.6.6, 16.7 prior to 16.7.4, and 16.8 prior to 16.8.1. An unauthorized attacker is able to assign arbitrary users to MRs that they created within the project

## References
- https://about.gitlab.com/releases/2024/01/25/critical-security-release-gitlab-16-8-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/430726
- https://nvd.nist.gov/vuln/detail/CVE-2024-0456
