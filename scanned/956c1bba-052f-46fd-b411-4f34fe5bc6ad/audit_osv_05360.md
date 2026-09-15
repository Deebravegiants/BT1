# [M] BIT-gitlab-2023-2013

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-2013
Aliases: CVE-2023-2013
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-2013
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.0.0 <16.0.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 1.2 before 15.10.8, all versions starting from 15.11 before 15.11.7, all versions starting from 16.0 before 16.0.2. An issue was found that allows someone to abuse a discrepancy between the Web application display and the git command line interface to social engineer victims into cloning non-trusted code.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-2013.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/406844
- https://hackerone.com/reports/1940441
- https://nvd.nist.gov/vuln/detail/CVE-2023-2013
