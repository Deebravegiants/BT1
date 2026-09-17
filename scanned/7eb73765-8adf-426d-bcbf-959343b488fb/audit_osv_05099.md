# [M] BIT-gitlab-2021-39874

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39874
Aliases: CVE-2021-39874
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39874
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.3.0 <14.3.1

## Details
In all versions of GitLab CE/EE since version 11.0, the requirement to enforce 2FA is not honored when using git commands.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39874.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/222527
- https://hackerone.com/reports/898477
- https://nvd.nist.gov/vuln/detail/CVE-2021-39874
