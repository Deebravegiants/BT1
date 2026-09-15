# [M] BIT-gitlab-2021-22251

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-22251
Aliases: CVE-2021-22251
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22251
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.1.0 <14.1.2

## Details
Improper validation of invited users' email address in GitLab EE affecting all versions since 12.2 allowed projects to add members with email address domain that should be blocked by group settings

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22251.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/14004
- https://hackerone.com/reports/679567
- https://nvd.nist.gov/vuln/detail/CVE-2021-22251
