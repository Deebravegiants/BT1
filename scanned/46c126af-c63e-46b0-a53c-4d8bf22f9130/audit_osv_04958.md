# [M] BIT-gitlab-2020-13317

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-13317
Aliases: CVE-2020-13317
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13317
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.3.0 <13.3.4

## Details
A vulnerability was discovered in GitLab versions before 13.1.10, 13.2.8, and 13.3.4. An insufficient check in the GraphQL api allowed a maintainer to delete a repository.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13317.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/215703
- https://hackerone.com/reports/858671
- https://nvd.nist.gov/vuln/detail/CVE-2020-13317
