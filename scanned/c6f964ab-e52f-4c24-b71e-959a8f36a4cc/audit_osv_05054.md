# [M] BIT-gitlab-2021-22219

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-22219
Aliases: CVE-2021-22219
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22219
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.12.0 <13.12.2

## Details
All versions of GitLab CE/EE starting from 9.5 before 13.10.5, all versions starting from 13.11 before 13.11.5, and all versions starting from 13.12 before 13.12.2 allow a high privilege user to obtain sensitive information from log files because the sensitive information was not correctly registered for log masking.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22219.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/296995
- https://nvd.nist.gov/vuln/detail/CVE-2021-22219
