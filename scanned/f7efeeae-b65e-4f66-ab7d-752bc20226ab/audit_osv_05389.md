# [H] Improper User Management in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2023-3907
Aliases: CVE-2023-3907
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-3907
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.6.0 <16.6.2

## Details
A privilege escalation vulnerability in GitLab EE affecting all versions from 16.0 prior to 16.4.4, 16.5 prior to 16.5.4, and 16.6 prior to 16.6.2 allows a project Maintainer to use a Project Access Token to escalate their role to Owner

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/418878
- https://hackerone.com/reports/2058934
- https://nvd.nist.gov/vuln/detail/CVE-2023-3907
