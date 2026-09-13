# [C] BIT-gitlab-2023-2825

## Summary
Severity: Critical
Advisory: BIT-gitlab-2023-2825
Aliases: CVE-2023-2825
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-2825
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.0.0 <16.0.1

## Details
An issue has been discovered in GitLab CE/EE affecting only version 16.0.0. An unauthenticated malicious user can use a path traversal vulnerability to read arbitrary files on the server when an attachment exists in a public project nested within at least five groups.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-2825.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/412371
- https://hackerone.com/reports/1994725
- https://nvd.nist.gov/vuln/detail/CVE-2023-2825
