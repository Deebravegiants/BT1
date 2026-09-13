# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-5846
Aliases: CVE-2025-5846
Ecosystem: Bitnami
Published: 2025-06-30
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-5846
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.1.0 <18.0.1

## Details
An issue has been discovered in GitLab EE affecting all versions from 16.10 before 17.11.5, 18.0 before 18.0.3, and 18.1 before 18.1.1 that could have allowed authenticated users to assign unrelated compliance frameworks to projects by sending crafted GraphQL mutations that bypassed framework-specific permission checks.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/546435
- https://nvd.nist.gov/vuln/detail/CVE-2025-5846
