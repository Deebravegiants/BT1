# [M] BIT-gitlab-2021-22253

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-22253
Aliases: CVE-2021-22253
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22253
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.1.0 <14.1.2

## Details
Improper authorization in GitLab EE affecting all versions since 13.4 allowed a user who previously had the necessary access to trigger deployments to protected environments under specific conditions after the access has been removed

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22253.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/323794
- https://hackerone.com/reports/1113783
- https://nvd.nist.gov/vuln/detail/CVE-2021-22253
