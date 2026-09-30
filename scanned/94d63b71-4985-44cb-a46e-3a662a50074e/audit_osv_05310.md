# [M] BIT-gitlab-2022-4131

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-4131
Aliases: CVE-2022-4131
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-4131
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.7.0 <15.7.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 10.8 before 15.5.7, all versions starting from 15.6 before 15.6.4, all versions starting from 15.7 before 15.7.2. An attacker may cause Denial of Service on a GitLab instance by exploiting a regex issue in how the application parses user agents.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-4131.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/383598
- https://hackerone.com/reports/1772063
- https://nvd.nist.gov/vuln/detail/CVE-2022-4131
