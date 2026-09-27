# [H] BIT-gitlab-2022-3759

## Summary
Severity: High
Advisory: BIT-gitlab-2022-3759
Aliases: CVE-2022-3759
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3759
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.8.0 <15.8.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 14.3 before 15.6.7, all versions starting from 15.7 before 15.7.6, all versions starting from 15.8 before 15.8.1. An attacker may upload a crafted CI job artifact zip file in a project that uses dynamic child pipelines and make a sidekiq job allocate a lot of memory. In GitLab instances where Sidekiq is memory-limited, this may cause Denial of Service.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3759.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/379633
- https://hackerone.com/reports/1736230
- https://nvd.nist.gov/vuln/detail/CVE-2022-3759
