# [M] BIT-gitlab-2020-26415

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-26415
Aliases: CVE-2020-26415
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-26415
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.6.0 <13.6.2

## Details
Information about the starred projects for private user profiles was exposed via the GraphQL API starting from 12.2 via the REST API. This affects GitLab >=12.2 to <13.4.7, >=13.5 to <13.5.5, and >=13.6 to <13.6.2.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-26415.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/277337
- https://nvd.nist.gov/vuln/detail/CVE-2020-26415
