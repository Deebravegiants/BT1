# [C] Incorrect Ownership Assignment in GitLab

## Summary
Severity: Critical
Advisory: BIT-gitlab-2023-4008
Aliases: CVE-2023-4008
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-4008
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.2.0 <16.2.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 15.9 before 16.0.8, all versions starting from 16.1 before 16.1.3, all versions starting from 16.2 before 16.2.2. It was possible to takeover GitLab Pages with unique domain URLs if the random string added was known.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/415942
- https://nvd.nist.gov/vuln/detail/CVE-2023-4008
