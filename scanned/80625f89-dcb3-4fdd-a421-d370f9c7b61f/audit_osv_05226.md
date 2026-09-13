# [M] BIT-gitlab-2022-2228

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-2228
Aliases: CVE-2022-2228
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2228
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.1.0 <15.1.1

## Details
Information exposure in GitLab EE affecting all versions from 12.0 prior to 14.10.5, 15.0 prior to 15.0.4, and 15.1 prior to 15.1.1 allows an attacker with the appropriate access tokens to obtain CI variables in a group with using IP-based access restrictions even if the GitLab Runner is calling from outside the allowed IP range

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2228.json
- https://gitlab.com/gitlab-org/security/gitlab/-/issues/682
- https://nvd.nist.gov/vuln/detail/CVE-2022-2228
