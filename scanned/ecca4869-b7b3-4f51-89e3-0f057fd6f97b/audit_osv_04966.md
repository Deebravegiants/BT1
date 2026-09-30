# [H] BIT-gitlab-2020-13325

## Summary
Severity: High
Advisory: BIT-gitlab-2020-13325
Aliases: CVE-2020-13325
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13325
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.1.0 <13.1.2

## Details
A vulnerability was discovered in GitLab versions prior 13.1. The comment section of the issue page was not restricting the characters properly, potentially resulting in a denial of service.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13325.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/215978
- https://nvd.nist.gov/vuln/detail/CVE-2020-13325
