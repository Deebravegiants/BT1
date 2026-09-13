# [H] BIT-gitlab-2023-0518

## Summary
Severity: High
Advisory: BIT-gitlab-2023-0518
Aliases: CVE-2023-0518
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-0518
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.8.0 <15.8.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 14.0 before 15.6.7, all versions starting from 15.7 before 15.7.6, all versions starting from 15.8 before 15.8.1. It was possible to trigger a DoS attack by uploading a malicious Helm chart.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-0518.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/383082
- https://hackerone.com/reports/1766973
- https://nvd.nist.gov/vuln/detail/CVE-2023-0518
