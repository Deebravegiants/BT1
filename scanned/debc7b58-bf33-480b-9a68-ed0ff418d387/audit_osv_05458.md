# [H] Missing Authorization in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2024-8114
Aliases: CVE-2024-8114
Ecosystem: Bitnami
Published: 2024-11-28
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-8114
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.6.0 <17.6.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions from 8.12 before 17.4.5, 17.5 before 17.5.3, and 17.6 before 17.6.1. This issue allows an attacker with access to a victim's Personal Access Token (PAT) to escalate privileges.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/480494
- https://hackerone.com/reports/2649822
- https://nvd.nist.gov/vuln/detail/CVE-2024-8114
