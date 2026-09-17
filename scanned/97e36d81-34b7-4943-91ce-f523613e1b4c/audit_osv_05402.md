# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-4700
Aliases: CVE-2023-4700
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-4700
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.5.0 <16.5.1

## Details
An authorization issue affecting GitLab EE affecting all versions from 14.7 prior to 16.3.6, 16.4 prior to 16.4.2, and 16.5 prior to 16.5.1, allowed a user to run jobs in protected environments, bypassing any required approvals.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/421937
- https://hackerone.com/reports/2129826
- https://nvd.nist.gov/vuln/detail/CVE-2023-4700
