# [H] BIT-gitlab-2022-4167

## Summary
Severity: High
Advisory: BIT-gitlab-2022-4167
Aliases: CVE-2022-4167
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-4167
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.7.0 <15.7.2

## Details
Incorrect Authorization check affecting all versions of GitLab EE from 13.11 prior to 15.5.7, 15.6 prior to 15.6.4, and 15.7 prior to 15.7.2 allows group access tokens to continue working even after the group owner loses the ability to revoke them.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-4167.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/367740
- https://nvd.nist.gov/vuln/detail/CVE-2022-4167
