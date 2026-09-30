# [M] BIT-gitlab-2021-39888

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39888
Aliases: CVE-2021-39888
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39888
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.3.0 <14.3.1

## Details
In all versions of GitLab EE starting from 13.10 before 14.1.7, all versions starting from 14.2 before 14.2.5, and all versions starting from 14.3 before 14.3.1 a specific API endpoint may reveal details about a private group and other sensitive info inside issue and merge request templates.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39888.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/336446
- https://hackerone.com/reports/1255128
- https://nvd.nist.gov/vuln/detail/CVE-2021-39888
