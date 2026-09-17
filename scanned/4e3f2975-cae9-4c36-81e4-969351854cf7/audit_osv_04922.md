# [H] BIT-gitlab-2020-13270

## Summary
Severity: High
Advisory: BIT-gitlab-2020-13270
Aliases: CVE-2020-13270
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13270
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.0.0 <13.0.1

## Details
Missing permission check on fork relation creation in GitLab CE/EE 11.3 and later through 13.0.1 allows guest users to create a fork relation on restricted public projects via API

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13270.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/24648
- https://hackerone.com/reports/419977
- https://nvd.nist.gov/vuln/detail/CVE-2020-13270
