# [H] BIT-gitlab-2023-2199

## Summary
Severity: High
Advisory: BIT-gitlab-2023-2199
Aliases: CVE-2023-2199
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-2199
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.0.0 <16.0.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 12.0 before 15.10.8, all versions starting from 15.11 before 15.11.7, all versions starting from 16.0 before 16.0.2. A Regular Expression Denial of Service was possible via sending crafted payloads to the preview_markdown endpoint.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-2199.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/408272
- https://hackerone.com/reports/1943819
- https://nvd.nist.gov/vuln/detail/CVE-2023-2199
