# [M] BIT-gitlab-2023-1098

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-1098
Aliases: CVE-2023-1098
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-1098
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.10.0 <15.10.1

## Details
An information disclosure vulnerability has been discovered in GitLab EE/CE affecting all versions starting from 11.5 before 15.8.5, all versions starting from 15.9 before 15.9.4, all versions starting from 15.10 before 15.10.1 will allow an admin to leak password from repository mirror configuration.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-1098.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/383745
- https://hackerone.com/reports/1784294
- https://nvd.nist.gov/vuln/detail/CVE-2023-1098
