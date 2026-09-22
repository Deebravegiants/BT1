# [M] BIT-gitlab-2022-2499

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-2499
Aliases: CVE-2022-2499
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2499
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.2.0 <15.2.1

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 13.10 before 15.0.5, all versions starting from 15.1 before 15.1.4, all versions starting from 15.2 before 15.2.1. GitLab's Jira integration has an insecure direct object reference vulnerability that may be exploited by an attacker to leak Jira issues.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2499.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/360800
- https://hackerone.com/reports/1538068
- https://nvd.nist.gov/vuln/detail/CVE-2022-2499
