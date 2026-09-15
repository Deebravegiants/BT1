# [M] Loop with Unreachable Exit Condition ('Infinite Loop') in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-5825
Aliases: CVE-2023-5825
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-5825
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.5.0 <16.5.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 16.2 before 16.3.6, all versions starting from 16.4 before 16.4.2, all versions starting from 16.5 before 16.5.1. A low-privileged attacker can point a CI/CD Component to an incorrect path and cause the server to exhaust all available memory through an infinite loop and cause Denial of Service.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/428984
- https://hackerone.com/reports/2218566
- https://nvd.nist.gov/vuln/detail/CVE-2023-5825
