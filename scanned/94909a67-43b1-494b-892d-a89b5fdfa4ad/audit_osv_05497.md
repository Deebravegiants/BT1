# [H] Incorrect Authorization in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2025-2242
Aliases: CVE-2025-2242
Ecosystem: Bitnami
Published: 2025-03-29
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-2242
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.4.0 <17.10.1

## Details
An improper access control vulnerability in GitLab CE/EE affecting all versions from 17.4 prior to 17.8.6, 17.9 prior to 17.9.3, and 17.10 prior to 17.10.1 allows a user who was an instance admin before but has since been downgraded to a regular user to continue to maintain elevated privileges to groups and projects.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/516271
- https://nvd.nist.gov/vuln/detail/CVE-2025-2242
