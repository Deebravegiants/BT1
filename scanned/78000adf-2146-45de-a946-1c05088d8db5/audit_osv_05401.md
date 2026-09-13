# [M] Missing Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-4630
Aliases: CVE-2023-4630
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-4630
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.3.0 <16.3.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 10.6 before 16.1.5, all versions starting from 16.2 before 16.2.5, all versions starting from 16.3 before 16.3.1 in which any user can read limited information about any project's imports.

## References
- https://about.gitlab.com/releases/2023/08/31/security-release-gitlab-16-3-1-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/415117
- https://nvd.nist.gov/vuln/detail/CVE-2023-4630
