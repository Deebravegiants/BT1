# [H] Missing Authorization in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2025-10871
Aliases: CVE-2025-10871
Ecosystem: Bitnami
Published: 2025-10-01
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-10871
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.4.0 <18.4.1

## Details
An issue has been discovered in GitLab EE affecting all versions from 16.6 before 18.2.7, 18.3 before 18.3.3, and 18.4 before 18.4.1. Project Maintainers can exploit a vulnerability where they can assign custom roles to users with permissions exceeding their own, effectively granting themselves elevated privileges.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/569482
- https://nvd.nist.gov/vuln/detail/CVE-2025-10871
