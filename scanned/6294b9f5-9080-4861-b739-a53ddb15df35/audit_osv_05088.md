# [M] BIT-gitlab-2021-22262

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-22262
Aliases: CVE-2021-22262
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22262
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.2.0 <14.2.2

## Details
Missing access control in all GitLab versions starting from 13.12 before 14.0.9, all versions starting from 14.1 before 14.1.4, and all versions starting from 14.2 before 14.2.2 with Jira Cloud integration enabled allows Jira users without administrative privileges to add and remove Jira Connect Namespaces via the GitLab.com for Jira Cloud application configuration page

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22262.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/327062
- https://hackerone.com/reports/1147812
- https://nvd.nist.gov/vuln/detail/CVE-2021-22262
