# [M] BIT-gitlab-2021-39943

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39943
Aliases: CVE-2021-39943
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39943
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.5.0 <14.5.2

## Details
An authorization logic error in the External Status Check API in GitLab EE affecting all versions starting from 14.1 before 14.3.6, all versions starting from 14.4 before 14.4.4, all versions starting from 14.5 before 14.5.2, allowed a user to update the status of the check via an API call

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39943.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/343604
- https://hackerone.com/reports/1375393
- https://nvd.nist.gov/vuln/detail/CVE-2021-39943
