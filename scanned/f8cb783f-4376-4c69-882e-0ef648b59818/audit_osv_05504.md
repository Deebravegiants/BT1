# [M] Incorrect Permission Assignment for Critical Resource in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-5819
Aliases: CVE-2025-5819
Ecosystem: Bitnami
Published: 2025-08-18
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-5819
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.2.0 <18.2.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions from 15.7 before 18.0.6, 18.1 before 18.1.4, and 18.2 before 18.2.2 that could have allowed authenticated users with developer access to obtain ID tokens for protected branches under certain circumstances.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/548165
- https://hackerone.com/reports/3137660
- https://nvd.nist.gov/vuln/detail/CVE-2025-5819
