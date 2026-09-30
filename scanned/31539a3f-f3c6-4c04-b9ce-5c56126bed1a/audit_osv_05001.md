# [M] BIT-gitlab-2020-26411

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-26411
Aliases: CVE-2020-26411
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-26411
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.6.0 <13.6.2

## Details
A potential DOS vulnerability was discovered in all versions of Gitlab starting from 13.4.x (>=13.4 to <13.4.7, >=13.5 to <13.5.5, and >=13.6 to <13.6.2). Using a specific query name for a project search can cause statement timeouts that can lead to a potential DOS if abused.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-26411.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/260330
- https://nvd.nist.gov/vuln/detail/CVE-2020-26411
