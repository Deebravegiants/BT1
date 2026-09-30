# [M] BIT-gitlab-2022-3288

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-3288
Aliases: CVE-2022-3288
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3288
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.4.0 <15.4.1

## Details
A branch/tag name confusion in GitLab CE/EE affecting all versions prior to 15.2.5, 15.3 prior to 15.3.4, and 15.4 prior to 15.4.1 allows an attacker to manipulate pages where the content of the default branch would be expected.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3288.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/354948
- https://hackerone.com/reports/1498354
- https://nvd.nist.gov/vuln/detail/CVE-2022-3288
