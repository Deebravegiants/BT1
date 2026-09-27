# [H] Privilege Chaining in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2024-1299
Aliases: CVE-2024-1299
Ecosystem: Bitnami
Published: 2024-03-12
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-1299
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.9.0 <16.9.2

## Details
A privilege escalation vulnerability was discovered in GitLab affecting versions 16.8 prior to 16.8.4 and 16.9 prior to 16.9.2. It was possible for a user with custom role of `manage_group_access_tokens` to rotate group access tokens with owner privileges.

## References
- https://about.gitlab.com/releases/2024/03/06/security-release-gitlab-16-9-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/440745
- https://hackerone.com/reports/2356976
- https://nvd.nist.gov/vuln/detail/CVE-2024-1299
