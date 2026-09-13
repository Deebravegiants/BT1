# [M] Privilege Chaining in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-1250
Aliases: CVE-2024-1250
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-1250
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.8.0 <16.8.2

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 16.8 before 16.8.2. When a user is assigned a custom role with manage_group_access_tokens permission, they may be able to create group access tokens with Owner privileges, which may lead to privilege escalation.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/439175
- https://nvd.nist.gov/vuln/detail/CVE-2024-1250
