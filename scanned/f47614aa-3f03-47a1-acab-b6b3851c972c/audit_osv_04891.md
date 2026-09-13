# [M] BIT-gitlab-2020-10079

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-10079
Aliases: CVE-2020-10079
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-10079
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=7.10.0 <12.8.2

## Details
GitLab 7.10 through 12.8.1 has Incorrect Access Control. Under certain conditions where users should have been required to configure two-factor authentication, it was not being required.

## References
- https://about.gitlab.com/releases/2020/03/04/gitlab-12-dot-8-dot-2-released/
- https://about.gitlab.com/releases/2020/03/04/gitlab-12-dot-8-dot-2-released/index.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-10079
