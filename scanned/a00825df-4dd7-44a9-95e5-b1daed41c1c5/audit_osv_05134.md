# [M] BIT-gitlab-2021-39916

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39916
Aliases: CVE-2021-39916
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39916
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.5.0 <14.5.2

## Details
Lack of an access control check in the External Status Check feature allowed any authenticated user to retrieve the configuration of any External Status Check in GitLab EE starting from 14.1 before 14.3.6, all versions starting from 14.4 before 14.4.4, all versions starting from 14.5 before 14.5.2.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39916.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/343379
- https://hackerone.com/reports/1372216
- https://nvd.nist.gov/vuln/detail/CVE-2021-39916
