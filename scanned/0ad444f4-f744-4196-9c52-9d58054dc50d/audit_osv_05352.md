# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-1555
Aliases: CVE-2023-1555
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-1555
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.3.0 <16.3.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 15.2 before 16.1.5, all versions starting from 16.2 before 16.2.5, all versions starting from 16.3 before 16.3.1. A namespace-level banned user can access the API.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/398587
- https://hackerone.com/reports/1911908
- https://nvd.nist.gov/vuln/detail/CVE-2023-1555
