# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2025-0652
Aliases: CVE-2025-0652
Ecosystem: Bitnami
Published: 2025-03-15
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-0652
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.9.0 <17.9.2

## Details
An issue has been discovered in GitLab EE/CE affecting all versions starting from 16.9 before 17.7.7, all versions starting from 17.8 before 17.8.5, all versions starting from 17.9 before 17.9.2 could allow unauthorized users to access confidential information intended for internal use only.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/514532
- https://hackerone.com/reports/2947863
- https://nvd.nist.gov/vuln/detail/CVE-2025-0652
