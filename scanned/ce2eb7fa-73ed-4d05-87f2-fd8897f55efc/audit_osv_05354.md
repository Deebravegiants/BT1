# [C] BIT-gitlab-2023-1708

## Summary
Severity: Critical
Advisory: BIT-gitlab-2023-1708
Aliases: CVE-2023-1708
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-1708
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.10.0 <15.10.1

## Details
An issue was identified in GitLab CE/EE affecting all versions from 1.0 prior to 15.8.5, 15.9 prior to 15.9.4, and 15.10 prior to 15.10.1 where non-printable characters gets copied from clipboard, allowing unexpected commands to be executed on victim machine.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-1708.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/387185
- https://hackerone.com/reports/1805604
- https://nvd.nist.gov/vuln/detail/CVE-2023-1708
