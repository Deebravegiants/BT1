# [M] BIT-gitlab-2022-3818

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-3818
Aliases: CVE-2022-3818
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3818
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.5.0 <15.5.2

## Details
An uncontrolled resource consumption issue when parsing URLs in GitLab CE/EE affecting all versions prior to 15.3.5, 15.4 prior to 15.4.4, and 15.5 prior to 15.5.2 allows an attacker to cause performance issues and potentially a denial of service on the GitLab instance.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3818.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/358170
- https://nvd.nist.gov/vuln/detail/CVE-2022-3818
