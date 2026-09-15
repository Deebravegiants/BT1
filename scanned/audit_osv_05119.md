# [M] BIT-gitlab-2021-39898

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39898
Aliases: CVE-2021-39898
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39898
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.3.0 <14.3.1

## Details
In all versions of GitLab CE/EE since version 10.6, a project export leaks the external webhook token value which may allow access to the project which it was exported from.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39898.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/33734
- https://hackerone.com/reports/698068
- https://nvd.nist.gov/vuln/detail/CVE-2021-39898
