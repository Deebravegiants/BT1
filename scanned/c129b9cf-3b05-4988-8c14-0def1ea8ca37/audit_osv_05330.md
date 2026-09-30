# [M] BIT-gitlab-2023-0155

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-0155
Aliases: CVE-2023-0155
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-0155
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.7.0 <15.10.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions before 15.8.5, 15.9.4, 15.10.1. Open redirects was possible due to framing arbitrary content on any page allowing user controlled markdown

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-0155.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/387638
- https://hackerone.com/reports/1817250
- https://nvd.nist.gov/vuln/detail/CVE-2023-0155
