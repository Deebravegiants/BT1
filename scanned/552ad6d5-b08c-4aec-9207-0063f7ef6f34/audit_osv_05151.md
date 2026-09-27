# [M] BIT-gitlab-2021-39942

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39942
Aliases: CVE-2021-39942
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39942
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.5.0 <14.5.2

## Details
A denial of service vulnerability in GitLab CE/EE affecting all versions starting from 12.0 before 14.3.6, all versions starting from 14.4 before 14.4.4, all versions starting from 14.5 before 14.5.2, allows low-privileged users to bypass file size limits in the NPM package repository to potentially cause denial of service.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39942.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/297492
- https://hackerone.com/reports/1071861
- https://nvd.nist.gov/vuln/detail/CVE-2021-39942
