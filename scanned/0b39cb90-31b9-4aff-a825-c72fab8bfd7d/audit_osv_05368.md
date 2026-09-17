# [H] BIT-gitlab-2023-2182

## Summary
Severity: High
Advisory: BIT-gitlab-2023-2182
Aliases: CVE-2023-2182
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-2182
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.11.0 <15.11.1

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 15.10 before 15.10.5, all versions starting from 15.11 before 15.11.1. Under certain conditions when OpenID Connect is enabled on an instance, it may allow users who are marked as 'external' to become 'regular' users thus leading to privilege escalation for those users.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-2182.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/403012
- https://nvd.nist.gov/vuln/detail/CVE-2023-2182
