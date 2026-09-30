# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-0516
Aliases: CVE-2025-0516
Ecosystem: Bitnami
Published: 2025-02-17
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-0516
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.7.0 <17.8.2

## Details
Improper Authorization in GitLab CE/EE affecting all versions from 17.7 prior to 17.7.4, 17.8 prior to 17.8.2 allow users with limited permissions to perform unauthorized actions on critical project data.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/513540
- https://hackerone.com/reports/2914644
- https://nvd.nist.gov/vuln/detail/CVE-2025-0516
