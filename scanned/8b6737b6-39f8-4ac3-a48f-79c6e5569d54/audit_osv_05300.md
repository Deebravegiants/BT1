# [M] BIT-gitlab-2022-3793

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-3793
Aliases: CVE-2022-3793
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3793
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.5.0 <15.5.2

## Details
An improper authorization issue in GitLab CE/EE affecting all versions from 14.4 prior to 15.3.5, 15.4 prior to 15.4.4, and 15.5 prior to 15.5.2 allows an attacker to read variables set directly in a GitLab CI/CD configuration file they don't have access to.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3793.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/372120
- https://nvd.nist.gov/vuln/detail/CVE-2022-3793
