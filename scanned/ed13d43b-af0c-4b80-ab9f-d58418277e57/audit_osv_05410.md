# [H] Improper Control of Generation of Code ('Code Injection') in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2023-5226
Aliases: CVE-2023-5226
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-5226
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.6.0 <16.6.1

## Details
An issue has been discovered in GitLab affecting all versions before 16.4.3, all versions starting from 16.5 before 16.5.3, all versions starting from 16.6 before 16.6.1. Under certain circumstances, a malicious actor bypass prohibited branch checks using a specially crafted branch name to manipulate repository content in the UI.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/426400
- https://hackerone.com/reports/2173053
- https://nvd.nist.gov/vuln/detail/CVE-2023-5226
