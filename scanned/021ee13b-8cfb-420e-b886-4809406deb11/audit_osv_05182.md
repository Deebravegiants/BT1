# [M] BIT-gitlab-2022-0740

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-0740
Aliases: CVE-2022-0740
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0740
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.9.0 <14.9.2

## Details
Incorrect authorization in the Asana integration's branch restriction feature in all versions of GitLab CE/EE starting from version 7.8.0 before 14.7.7, all versions starting from 14.8 before 14.8.5, all versions starting from 14.9 before 14.9.2 makes it possible to close Asana tasks from unrestricted branches.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0740.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/349359
- https://hackerone.com/reports/1411216
- https://nvd.nist.gov/vuln/detail/CVE-2022-0740
