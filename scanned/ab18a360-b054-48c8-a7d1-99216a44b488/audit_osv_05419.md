# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-6955
Aliases: CVE-2023-6955
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-6955
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.7.0 <16.7.2

## Details
A missing authorization check vulnerability exists in GitLab Remote Development affecting all versions prior to 16.5.6, 16.6 prior to 16.6.4 and 16.7 prior to 16.7.2. This condition allows an attacker to create a workspace in one group that is associated with an agent from another group.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/432188
- https://nvd.nist.gov/vuln/detail/CVE-2023-6955
