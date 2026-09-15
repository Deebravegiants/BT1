# [M] BIT-gitlab-2022-3870

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-3870
Aliases: CVE-2022-3870
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3870
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.7.0 <15.7.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 10.0 before 15.5.7, all versions starting from 15.6 before 15.6.4, all versions starting from 15.7 before 15.7.2. GitLab allows unauthenticated users to download user avatars using the victim's user ID, on private instances that restrict public level visibility.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3870.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/381647
- https://hackerone.com/reports/1753423
- https://nvd.nist.gov/vuln/detail/CVE-2022-3870
