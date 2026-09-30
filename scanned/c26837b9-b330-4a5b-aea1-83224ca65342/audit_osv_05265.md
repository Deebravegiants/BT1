# [H] BIT-gitlab-2022-3031

## Summary
Severity: High
Advisory: BIT-gitlab-2022-3031
Aliases: CVE-2022-3031
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3031
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.3.0 <15.3.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions before 15.1.6, all versions starting from 15.2 before 15.2.4, all versions starting from 15.3 before 15.3.2. It may be possible for an attacker to guess a user's password by brute force by sending crafted requests to a specific endpoint, even if the victim user has 2FA enabled on their account.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3031.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/340395
- https://nvd.nist.gov/vuln/detail/CVE-2022-3031
