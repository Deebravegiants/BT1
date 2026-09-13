# [M] BIT-gitlab-2021-39934

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39934
Aliases: CVE-2021-39934
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39934
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.5.0 <14.5.2

## Details
Improper access control allows any project member to retrieve the service desk email address in GitLab CE/EE versions starting 12.10 before 14.3.6, all versions starting from 14.4 before 14.4.4, all versions starting from 14.5 before 14.5.2.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39934.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/342823
- https://hackerone.com/reports/1360744
- https://nvd.nist.gov/vuln/detail/CVE-2021-39934
