# [M] Improper Ownership Management in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-0989
Aliases: CVE-2023-0989
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-0989
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.4.0 <16.4.1

## Details
An information disclosure issue in GitLab CE/EE affecting all versions starting from 13.11 prior to 16.2.8, 16.3 prior to 16.3.5, and 16.4 prior to 16.4.1 allows an attacker to extract non-protected CI/CD variables by tricking a user to visit a fork with a malicious CI/CD configuration.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/417275
- https://hackerone.com/reports/1875515
- https://nvd.nist.gov/vuln/detail/CVE-2023-0989
