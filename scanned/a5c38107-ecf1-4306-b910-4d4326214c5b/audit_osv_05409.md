# [H] Execution with Unnecessary Privileges in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2023-5207
Aliases: CVE-2023-5207
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-5207
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.4.0 <16.4.1

## Details
A vulnerability was discovered in GitLab CE and EE affecting all versions starting 16.0 prior to 16.2.8, 16.3 prior to 16.3.5, and 16.4 prior to 16.4.1. An authenticated attacker could perform arbitrary pipeline execution under the context of another user.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/425604
- https://gitlab.com/gitlab-org/gitlab/-/issues/425857
- https://hackerone.com/reports/2174141
- https://nvd.nist.gov/vuln/detail/CVE-2023-5207
