# [H] Missing Authorization in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2024-4660
Aliases: CVE-2024-4660
Ecosystem: Bitnami
Published: 2024-09-14
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-4660
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.3.0 <17.3.2

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 11.2 before 17.1.7, all versions starting from 17.2 before 17.2.5, all versions starting from 17.3 before 17.3.2. It was possible for a guest to read the source code of a private project by using group templates.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/460892
- https://hackerone.com/reports/2480126
- https://about.gitlab.com/releases/2024/09/11/patch-release-gitlab-17-3-2-released/
- https://nvd.nist.gov/vuln/detail/CVE-2024-4660
