# [M] Debug Messages Revealing Unnecessary Information in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-2469
Aliases: CVE-2025-2469
Ecosystem: Bitnami
Published: 2025-04-12
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-2469
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.9.0 <17.10.4

## Details
An issue has been discovered in GitLab CE/EE affecting all versions from 17.9 before 17.9.6, and 17.10 before 17.10.4. The runtime profiling data of a specific service was accessible to unauthenticated users.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/525374
- https://hackerone.com/reports/3030586
- https://nvd.nist.gov/vuln/detail/CVE-2025-2469
