# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-2246
Aliases: CVE-2025-2246
Ecosystem: Bitnami
Published: 2025-08-30
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-2246
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.3.0 <18.3.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions before 18.1.5, 18.2 before 18.2.5, and 18.3 before 18.3.1 that could have allowed unauthenticated users to access sensitive manual CI/CD variables by querying the GraphQL API.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/524592
- https://hackerone.com/reports/3026559
- https://nvd.nist.gov/vuln/detail/CVE-2025-2246
