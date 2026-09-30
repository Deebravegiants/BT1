# [M] BIT-gitlab-2023-1072

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-1072
Aliases: CVE-2023-1072
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-1072
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.9.0 <15.9.2

## Details
An issue has been discovered in GitLab affecting all versions starting from 9.0 before 15.7.8, all versions starting from 15.8 before 15.8.4, all versions starting from 15.9 before 15.9.2. It was possible to trigger a resource depletion attack due to improper filtering for number of requests to read commits details.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-1072.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/219619
- https://nvd.nist.gov/vuln/detail/CVE-2023-1072
