# [M] BIT-gitlab-2022-3291

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-3291
Aliases: CVE-2022-3291
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3291
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.4.0 <15.4.1

## Details
Serialization of sensitive data in GitLab EE affecting all versions from 14.9 prior to 15.2.5, 15.3 prior to 15.3.4, and 15.4 prior to 15.4.1 can leak sensitive information via cache

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3291.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/354299
- https://nvd.nist.gov/vuln/detail/CVE-2022-3291
