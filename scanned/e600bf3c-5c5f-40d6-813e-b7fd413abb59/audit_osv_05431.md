# [M] Insufficient Granularity of Access Control in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-11931
Aliases: CVE-2024-11931
Ecosystem: Bitnami
Published: 2025-01-28
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-11931
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.8.0 <17.8.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 17.0 prior to 17.6.4, from 17.7 prior to 17.7.3, and from 17.8 prior to 17.8.1. Under certain conditions, it may have been possible for users with developer role to exfiltrate protected CI variables via CI lint.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/480901
- https://about.gitlab.com/releases/2025/01/22/patch-release-gitlab-17-8-1-released/https://about.gitlab.com/releases/2025/01/22/patch-release-gitlab-17-8-1-released/
- https://nvd.nist.gov/vuln/detail/CVE-2024-11931
