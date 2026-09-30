# [H] BIT-gitlab-2022-0244

## Summary
Severity: High
Advisory: BIT-gitlab-2022-0244
Aliases: CVE-2022-0244
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0244
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.6.0 <14.6.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting with 14.5. Arbitrary file read was possible by importing a group was due to incorrect handling of file.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0244.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/349524
- https://hackerone.com/reports/1439593
- https://nvd.nist.gov/vuln/detail/CVE-2022-0244
