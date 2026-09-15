# [M] BIT-gitlab-2020-10081

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-10081
Aliases: CVE-2020-10081
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-10081
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=0 <12.8.2

## Details
GitLab before 12.8.2 has Incorrect Access Control. It was internally discovered that the LFS import process could potentially be used to incorrectly access LFS objects not owned by the user.

## References
- https://about.gitlab.com/releases/2020/03/04/gitlab-12-dot-8-dot-2-released/
- https://about.gitlab.com/releases/2020/03/04/gitlab-12-dot-8-dot-2-released/index.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-10081
