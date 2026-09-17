# [H] Authentication Bypass by Assumed-Immutable Data in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2024-4024
Aliases: CVE-2024-4024
Ecosystem: Bitnami
Published: 2024-04-27
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-4024
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.11.0 <16.11.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 7.8 before 16.9.6, all versions starting from 16.10 before 16.10.4, all versions starting from 16.11 before 16.11.1. Under certain conditions, an attacker with their Bitbucket account credentials may be able to take over a GitLab account linked to another user's Bitbucket account, if Bitbucket is used as an OAuth 2.0 provider on GitLab.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/452426
- https://nvd.nist.gov/vuln/detail/CVE-2024-4024
