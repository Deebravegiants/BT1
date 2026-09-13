# [M] BIT-gitlab-2020-13333

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-13333
Aliases: CVE-2020-13333
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13333
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.4.0 <13.4.2

## Details
A potential DOS vulnerability was discovered in GitLab versions 13.1, 13.2 and 13.3. The api to update an asset as a link from a release had a regex check which caused exponential number of backtracks for certain user supplied values resulting in high CPU usage.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13333.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/218753
- https://hackerone.com/reports/870820
- https://nvd.nist.gov/vuln/detail/CVE-2020-13333
