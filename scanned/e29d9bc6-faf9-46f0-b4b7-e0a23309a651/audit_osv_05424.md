# [M] Direct Request ('Forced Browsing') in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-0861
Aliases: CVE-2024-0861
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-0861
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.9.0 <16.9.1

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 16.4 before 16.7.6, all versions starting from 16.8 before 16.8.3, all versions starting from 16.9 before 16.9.1. Users with the `Guest` role can change `Custom dashboard projects` settings contrary to permissions.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/439240
- https://hackerone.com/reports/2316435
- https://nvd.nist.gov/vuln/detail/CVE-2024-0861
