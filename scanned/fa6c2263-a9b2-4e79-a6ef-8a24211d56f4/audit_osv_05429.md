# [H] Incorrect Authorization in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2024-11669
Aliases: CVE-2024-11669
Ecosystem: Bitnami
Published: 2024-11-28
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-11669
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.6.0 <17.6.1

## Details
An issue was discovered in GitLab CE/EE affecting all versions from 16.9.8 before 17.4.5, 17.5 before 17.5.3, and 17.6 before 17.6.1. Certain API endpoints could potentially allow unauthorized access to sensitive data due to overly broad application of token scopes.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/501528
- https://nvd.nist.gov/vuln/detail/CVE-2024-11669
