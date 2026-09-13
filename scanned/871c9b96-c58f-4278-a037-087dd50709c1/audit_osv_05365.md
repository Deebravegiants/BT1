# [H] BIT-gitlab-2023-2132

## Summary
Severity: High
Advisory: BIT-gitlab-2023-2132
Aliases: CVE-2023-2132
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-2132
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.0.0 <16.0.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 15.4 before 15.10.8, all versions starting from 15.11 before 15.11.7, all versions starting from 16.0 before 16.0.2. A DollarMathPostFilter Regular Expression Denial of Service in was possible by sending crafted payloads to the preview_markdown endpoint.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-2132.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/407586
- https://hackerone.com/reports/1934711
- https://nvd.nist.gov/vuln/detail/CVE-2023-2132
