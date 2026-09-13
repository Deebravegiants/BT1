# [H] Improper Enforcement of Behavioral Workflow in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2024-0410
Aliases: CVE-2024-0410
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-0410
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.9.0 <16.9.1

## Details
An authorization bypass vulnerability was discovered in GitLab affecting versions 15.1 prior to 16.7.6, 16.8 prior to 16.8.3, and 16.9 prior to 16.9.1. A developer could bypass CODEOWNERS approvals by creating a merge conflict.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/437988
- https://hackerone.com/reports/2296778
- https://nvd.nist.gov/vuln/detail/CVE-2024-0410
