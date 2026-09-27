# [M] BIT-gitlab-2020-13262

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-13262
Aliases: CVE-2020-13262
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13262
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.0.0 <13.0.1

## Details
Client-Side code injection through Mermaid markup in GitLab CE/EE 12.9 and later through 13.0.1 allows a specially crafted Mermaid payload to PUT requests on behalf of other users via clicking on a link

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13262.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/211949
- https://hackerone.com/reports/824689
- https://nvd.nist.gov/vuln/detail/CVE-2020-13262
