# [M] Incorrect Synchronization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-4278
Aliases: CVE-2024-4278
Ecosystem: Bitnami
Published: 2024-09-27
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-4278
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.4.0 <17.4.1

## Details
An information disclosure issue has been discovered in GitLab EE affecting all versions starting from 16.5 prior to 17.2.8, from 17.3 prior to 17.3.4, and from 17.4 prior to 17.4.1. A maintainer could obtain a Dependency Proxy password by editing a certain Dependency Proxy setting.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/458484
- https://hackerone.com/reports/2466205
- https://nvd.nist.gov/vuln/detail/CVE-2024-4278
