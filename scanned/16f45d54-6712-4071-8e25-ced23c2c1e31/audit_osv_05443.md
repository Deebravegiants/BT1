# [M] Improper Access Control in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-2191
Aliases: CVE-2024-2191
Ecosystem: Bitnami
Published: 2024-06-28
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-2191
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.1.0 <17.1.1

## Details
An issue was discovered in GitLab CE/EE affecting all versions starting from 16.9 prior to 16.11.5, starting from 17.0 prior to 17.0.3, and starting from 17.1 prior to 17.1.1, which allows merge request title to be visible publicly despite being set as project members only.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/444655
- https://hackerone.com/reports/2357370
- https://nvd.nist.gov/vuln/detail/CVE-2024-2191
