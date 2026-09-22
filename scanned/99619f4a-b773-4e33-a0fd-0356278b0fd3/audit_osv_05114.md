# [M] BIT-gitlab-2021-39892

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39892
Aliases: CVE-2021-39892
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39892
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.3.0 <14.3.1

## Details
In all versions of GitLab CE/EE since version 12.0, a lower privileged user can import users from projects that they don't have a maintainer role on and disclose email addresses of those users.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39892.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/28440
- https://hackerone.com/reports/542539
- https://nvd.nist.gov/vuln/detail/CVE-2021-39892
