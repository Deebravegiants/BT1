# [M] BIT-gitlab-2023-1710

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-1710
Aliases: CVE-2023-1710
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-1710
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.10.0 <15.10.1

## Details
A sensitive information disclosure vulnerability in GitLab affecting all versions from 15.0 prior to 15.8.5, 15.9 prior to 15.9.4 and 15.10 prior to 15.10.1 allows an attacker to view the count of internal notes for a given issue.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-1710.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/388242
- https://hackerone.com/reports/1829768
- https://nvd.nist.gov/vuln/detail/CVE-2023-1710
