# [M] BIT-gitlab-2020-10086

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-10086
Aliases: CVE-2020-10086
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-10086
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=10.4.0 <12.8.2

## Details
GitLab 10.4 through 12.8.1 allows Directory Traversal. A particular endpoint was vulnerable to a directory traversal vulnerability, leading to arbitrary file read.

## References
- https://about.gitlab.com/releases/2020/03/04/gitlab-12-dot-8-dot-2-released/
- https://about.gitlab.com/releases/2020/03/04/gitlab-12-dot-8-dot-2-released/index.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-10086
