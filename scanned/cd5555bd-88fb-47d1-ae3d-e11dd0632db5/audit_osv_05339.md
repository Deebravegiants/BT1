# [H] BIT-gitlab-2023-0805

## Summary
Severity: High
Advisory: BIT-gitlab-2023-0805
Aliases: CVE-2023-0805
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-0805
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.11.0 <15.11.1

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 15.2 before 15.9.6, all versions starting from 15.10 before 15.10.5, all versions starting from 15.11 before 15.11.1. A malicious group member may continue to have access to the public projects of a public group even after being banned from the public group by the owner.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-0805.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/391433
- https://hackerone.com/reports/1850046
- https://nvd.nist.gov/vuln/detail/CVE-2023-0805
