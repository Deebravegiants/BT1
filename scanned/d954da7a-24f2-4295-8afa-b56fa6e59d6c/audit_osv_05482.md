# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-11865
Aliases: CVE-2025-11865
Ecosystem: Bitnami
Published: 2025-11-20
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-11865
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.5.0 <18.5.2

## Details
An issue has been discovered in GitLab EE affecting all versions from 18.1 before 18.3.6, 18.4 before 18.4.4, and 18.5 before 18.5.2 that, under certain circumstances, could have allowed an attacker to remove Duo flows of another user.

## References
- https://about.gitlab.com/releases/2025/11/12/patch-release-gitlab-18-5-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/561399
- https://nvd.nist.gov/vuln/detail/CVE-2025-11865
