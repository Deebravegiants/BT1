# [M] BIT-gitlab-2022-0172

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-0172
Aliases: CVE-2022-0172
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0172
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.6.0 <14.6.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting with 12.3. Under certain conditions it was possible to bypass the IP restriction for public projects through GraphQL allowing unauthorised users to read titles of issues, merge requests and milestones.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0172.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/348411
- https://nvd.nist.gov/vuln/detail/CVE-2022-0172
