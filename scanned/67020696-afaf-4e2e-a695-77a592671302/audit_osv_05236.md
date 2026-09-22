# [H] BIT-gitlab-2022-2326

## Summary
Severity: High
Advisory: BIT-gitlab-2022-2326
Aliases: CVE-2022-2326
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2326
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.2.0 <15.2.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions before 15.0.5, all versions starting from 15.1 before 15.1.4, all versions starting from 15.2 before 15.2.1. It may be possible to gain access to a private project through an email invite by using other user's email address as an unverified secondary email.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2326.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/356665
- https://hackerone.com/reports/1517554
- https://nvd.nist.gov/vuln/detail/CVE-2022-2326
