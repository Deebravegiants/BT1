# [C] BIT-gitlab-2022-2185

## Summary
Severity: Critical
Advisory: BIT-gitlab-2022-2185
Aliases: CVE-2022-2185
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2185
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.1.0 <15.1.1

## Details
A critical issue has been discovered in GitLab affecting all versions starting from 14.0 prior to 14.10.5, 15.0 prior to 15.0.4, and 15.1 prior to 15.1.1 where an authenticated user authorized to import projects could import a maliciously crafted project leading to remote code execution.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2185.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/366088
- https://hackerone.com/reports/1609965
- https://nvd.nist.gov/vuln/detail/CVE-2022-2185
