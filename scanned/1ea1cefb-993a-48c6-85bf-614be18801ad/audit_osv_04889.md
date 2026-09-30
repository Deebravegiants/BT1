# [C] BIT-gitlab-2020-10077

## Summary
Severity: Critical
Advisory: BIT-gitlab-2020-10077
Aliases: CVE-2020-10077
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-10077
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=3.0.0 <12.8.2

## Details
GitLab EE 3.0 through 12.8.1 allows SSRF. An internal investigation revealed that a particular deprecated service was creating a server side request forgery risk.

## References
- https://about.gitlab.com/releases/2020/03/04/gitlab-12-dot-8-dot-2-released/
- https://about.gitlab.com/releases/2020/03/04/gitlab-12-dot-8-dot-2-released/index.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-10077
