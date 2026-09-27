# [M] BIT-gitlab-2021-39932

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39932
Aliases: CVE-2021-39932
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39932
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.5.0 <14.5.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 11.0 before 14.3.6, all versions starting from 14.4 before 14.4.4, all versions starting from 14.5 before 14.5.2. Using large payloads, the diff feature could be used to trigger high load time for users reviewing code changes.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39932.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/217360
- https://nvd.nist.gov/vuln/detail/CVE-2021-39932
