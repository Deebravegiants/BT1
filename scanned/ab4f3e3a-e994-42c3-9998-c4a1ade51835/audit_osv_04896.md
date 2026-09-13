# [M] BIT-gitlab-2020-10084

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-10084
Aliases: CVE-2020-10084
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-10084
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=11.6.0 <12.8.2

## Details
GitLab EE 11.6 through 12.8.1 allows Information Disclosure. Sending a specially crafted request to the vulnerability_feedback endpoint could result in the exposure of a private project namespace

## References
- https://about.gitlab.com/releases/2020/03/04/gitlab-12-dot-8-dot-2-released/
- https://about.gitlab.com/releases/2020/03/04/gitlab-12-dot-8-dot-2-released/index.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-10084
