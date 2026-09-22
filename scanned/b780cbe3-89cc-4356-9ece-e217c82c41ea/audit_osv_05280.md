# [M] BIT-gitlab-2022-3331

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-3331
Aliases: CVE-2022-3331
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3331
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.3.0 <15.3.2

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 14.5 before 15.1.6, all versions starting from 15.2 before 15.2.4, all versions starting from 15.3 before 15.3.2. GitLab's Zentao integration has an insecure direct object reference vulnerability that may be exploited by an attacker to leak Zentao project issues.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3331.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/360372
- https://hackerone.com/reports/1542834
- https://nvd.nist.gov/vuln/detail/CVE-2022-3331
