# [H] BIT-gitlab-2022-4037

## Summary
Severity: High
Advisory: BIT-gitlab-2022-4037
Aliases: CVE-2022-4037
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-4037
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.7.0 <15.7.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions before 15.5.7, all versions starting from 15.6 before 15.6.4, all versions starting from 15.7 before 15.7.2. A race condition can lead to verified email forgery and takeover of third-party accounts when using GitLab as an OAuth provider.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-4037.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/382957
- https://hackerone.com/reports/1772543
- https://nvd.nist.gov/vuln/detail/CVE-2022-4037
