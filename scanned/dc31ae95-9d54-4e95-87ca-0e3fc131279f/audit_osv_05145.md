# [M] BIT-gitlab-2021-39936

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39936
Aliases: CVE-2021-39936
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39936
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.5.0 <14.5.2

## Details
Improper access control in GitLab CE/EE affecting all versions starting from 10.7 before 14.3.6, all versions starting from 14.4 before 14.4.4, all versions starting from 14.5 before 14.5.2, allows an attacker in possession of a deploy token to access a project's disabled wiki.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39936.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/241767
- https://hackerone.com/reports/964057
- https://nvd.nist.gov/vuln/detail/CVE-2021-39936
