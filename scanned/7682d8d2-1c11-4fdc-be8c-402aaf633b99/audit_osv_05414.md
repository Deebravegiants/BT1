# [H] Incorrect Authorization in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2023-5995
Aliases: CVE-2023-5995
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-5995
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.6.0 <16.6.1

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 16.2 before 16.4.3, all versions starting from 16.5 before 16.5.3, all versions starting from 16.6 before 16.6.1. It was possible for an attacker to abuse the policy bot to gain access to internal projects.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/425361
- https://hackerone.com/reports/2138880
- https://nvd.nist.gov/vuln/detail/CVE-2023-5995
