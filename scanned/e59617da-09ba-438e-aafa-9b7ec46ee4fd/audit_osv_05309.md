# [H] BIT-gitlab-2022-4092

## Summary
Severity: High
Advisory: BIT-gitlab-2022-4092
Aliases: CVE-2022-4092
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-4092
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.6.0 <15.6.1

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 15.6 before 15.6.1. It was possible to create a malicious README page due to improper neutralisation of user supplied input.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-4092.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/383208
- https://hackerone.com/reports/1777934
- https://nvd.nist.gov/vuln/detail/CVE-2022-4092
