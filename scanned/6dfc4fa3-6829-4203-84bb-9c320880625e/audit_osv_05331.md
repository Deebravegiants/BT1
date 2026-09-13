# [M] BIT-gitlab-2023-0223

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-0223
Aliases: CVE-2023-0223
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-0223
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.9.0 <15.9.2

## Details
An issue has been discovered in GitLab affecting all versions starting from 15.5 before 15.7.8, all versions starting from 15.8 before 15.8.4, all versions starting from 15.9 before 15.9.2. Non-project members could retrieve release descriptions via the API, even if the release visibility is restricted to project members only in the project settings.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-0223.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/387870
- https://hackerone.com/reports/1824226
- https://nvd.nist.gov/vuln/detail/CVE-2023-0223
