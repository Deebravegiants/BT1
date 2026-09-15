# [M] Improper Encoding or Escaping of Output in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-2200
Aliases: CVE-2023-2200
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-2200
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.1.0 <16.1.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 7.14 before 15.11.10, all versions starting from 16.0 before 16.0.6, all versions starting from 16.1 before 16.1.1, which allows an attacker to inject HTML in an email address field.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/408281
- https://hackerone.com/reports/1935628
- https://nvd.nist.gov/vuln/detail/CVE-2023-2200
