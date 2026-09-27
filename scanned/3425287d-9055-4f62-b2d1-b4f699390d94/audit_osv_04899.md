# [H] BIT-gitlab-2020-10087

## Summary
Severity: High
Advisory: BIT-gitlab-2020-10087
Aliases: CVE-2020-10087
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-10087
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=0 <12.8.2

## Details
GitLab before 12.8.2 allows Information Disclosure. Badge images were not being proxied, causing mixed content warnings as well as leaking the IP address of the user.

## References
- https://about.gitlab.com/releases/2020/03/04/gitlab-12-dot-8-dot-2-released/
- https://about.gitlab.com/releases/2020/03/04/gitlab-12-dot-8-dot-2-released/index.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-10087
