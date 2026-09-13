# [H] BIT-gitlab-2022-1510

## Summary
Severity: High
Advisory: BIT-gitlab-2022-1510
Aliases: CVE-2022-1510
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1510
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.10.0 <14.10.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 13.9 before 14.8.6, all versions starting from 14.9 before 14.9.4, all versions starting from 14.10 before 14.10.1. GitLab was not correctly handling malicious text in the CI Editor and CI Pipeline details page allowing the attacker to cause uncontrolled resource consumption.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1510.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/343276
- https://hackerone.com/reports/1353058
- https://nvd.nist.gov/vuln/detail/CVE-2022-1510
