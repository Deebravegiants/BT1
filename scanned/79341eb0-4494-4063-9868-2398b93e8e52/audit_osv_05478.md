# [M] Business Logic Errors in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-10868
Aliases: CVE-2025-10868
Ecosystem: Bitnami
Published: 2025-10-01
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-10868
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=18.4.0 <18.4.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions from 17.4 before 18.2.7, 18.3 before 18.3.3, and 18.4 before 18.4.1 where certain string conversion methods exhibit performance degradation with large inputs.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/526482
- https://nvd.nist.gov/vuln/detail/CVE-2025-10868
