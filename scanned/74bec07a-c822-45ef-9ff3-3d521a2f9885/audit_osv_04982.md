# [M] BIT-gitlab-2020-13344

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-13344
Aliases: CVE-2020-13344
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13344
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.4.0 <13.4.2

## Details
An issue has been discovered in GitLab affecting all versions prior to 13.2.10, 13.3.7 and 13.4.2. Sessions keys are stored in plain-text in Redis which allows attacker with Redis access to authenticate as any user that has a session stored in Redis

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13344.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/17817
- https://nvd.nist.gov/vuln/detail/CVE-2020-13344
