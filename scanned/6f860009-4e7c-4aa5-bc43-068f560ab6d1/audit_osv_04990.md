# [M] BIT-gitlab-2020-13354

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-13354
Aliases: CVE-2020-13354
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13354
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=0 <13.3.9

## Details
A potential DOS vulnerability was discovered in GitLab CE/EE starting with version 12.6. The container registry name check could cause exponential number of backtracks for certain user supplied values resulting in high CPU usage. Affected versions are: >=12.6, <13.3.9.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13354.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/220019
- https://hackerone.com/reports/869875
- https://nvd.nist.gov/vuln/detail/CVE-2020-13354
