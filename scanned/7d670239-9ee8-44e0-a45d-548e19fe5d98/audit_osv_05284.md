# [M] BIT-gitlab-2022-3413

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-3413
Aliases: CVE-2022-3413
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3413
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.5.0 <15.5.2

## Details
Incorrect authorization during display of Audit Events in GitLab EE affecting all versions from 14.5 prior to 15.3.5, 15.4 prior to 15.4.4, and 15.5 prior to 15.5.2, allowed Developers to view the project's Audit Events and Developers or Maintainers to view the group's Audit Events. These should have been restricted to Project Maintainers, Group Owners, and above.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3413.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/374926
- https://nvd.nist.gov/vuln/detail/CVE-2022-3413
