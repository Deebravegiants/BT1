# [H] Incorrect Authorization in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2024-9693
Aliases: CVE-2024-9693
Ecosystem: Bitnami
Published: 2024-11-16
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-9693
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.5.0 <17.5.2

## Details
An issue was discovered in GitLab CE/EE affecting all versions starting from 16.0 prior to 17.3.7, starting from 17.4 prior to 17.4.4, and starting from 17.5 prior to 17.5.2, which could have allowed unauthorized access to the Kubernetes agent in a cluster under specific configurations.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/497449
- https://nvd.nist.gov/vuln/detail/CVE-2024-9693
