# [M] BIT-gitlab-2023-2181

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-2181
Aliases: CVE-2023-2181
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-2181
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.11.0 <15.11.3

## Details
An issue has been discovered in GitLab affecting all versions before 15.9.8, 15.10.0 before 15.10.7, and 15.11.0 before 15.11.3. A malicious developer could use a git feature called refs/replace to smuggle content into a merge request which would not be visible during review in the UI.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-2181.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/407859
- https://hackerone.com/reports/1938185
- https://nvd.nist.gov/vuln/detail/CVE-2023-2181
