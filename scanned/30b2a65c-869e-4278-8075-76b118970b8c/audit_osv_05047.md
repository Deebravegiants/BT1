# [M] BIT-gitlab-2021-22210

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-22210
Aliases: CVE-2021-22210
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22210
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.11.0 <13.11.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 13.2. When querying the repository branches through API, GitLab was ignoring a query parameter and returning a considerable amount of results.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22210.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/322500
- https://nvd.nist.gov/vuln/detail/CVE-2021-22210
