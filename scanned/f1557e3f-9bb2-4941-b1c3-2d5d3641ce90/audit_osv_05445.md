# [M] Improper Neutralization of Input Used for LLM Prompting in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-3303
Aliases: CVE-2024-3303
Ecosystem: Bitnami
Published: 2025-02-17
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-3303
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.0.0 <17.8.2

## Details
An issue was discovered in GitLab EE affecting all versions starting from 16.0 prior to 17.6.5, starting from 17.7 prior to 17.7.4, and starting from 17.8 prior to 17.8.2, which allows an attacker to exfiltrate contents of a private issue using prompt injection.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/454460
- https://hackerone.com/reports/2418620
- https://nvd.nist.gov/vuln/detail/CVE-2024-3303
