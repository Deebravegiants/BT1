# [M] BIT-gitlab-2022-1100

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-1100
Aliases: CVE-2022-1100
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1100
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.9.0 <14.9.2

## Details
A potential DOS vulnerability was discovered in GitLab CE/EE affecting all versions from 13.1 prior to 14.7.7, 14.8.0 prior to 14.8.5, and 14.9.0 prior to 14.9.2. The api to update an asset as a link from a release had a regex check which caused exponential number of backtracks for certain user supplied values resulting in high CPU usage.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1100.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/273771
- https://nvd.nist.gov/vuln/detail/CVE-2022-1100
