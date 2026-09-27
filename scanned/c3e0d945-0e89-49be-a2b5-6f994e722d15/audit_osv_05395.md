# [H] Insertion of Sensitive Information into Log File in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2023-3993
Aliases: CVE-2023-3993
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-3993
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.2.0 <16.2.2

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 14.3 before 16.0.8, all versions starting from 16.1 before 16.1.3, all versions starting from 16.2 before 16.2.2. Access tokens may have been logged when a query was made to a specific endpoint.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/409570
- https://nvd.nist.gov/vuln/detail/CVE-2023-3993
