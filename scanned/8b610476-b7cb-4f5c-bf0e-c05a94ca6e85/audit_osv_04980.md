# [M] BIT-gitlab-2020-13341

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-13341
Aliases: CVE-2020-13341
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13341
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.4.0 <13.4.2

## Details
An issue has been discovered in GitLab affecting all versions prior to 13.2.10, 13.3.7 and 13.4.2. Insufficient permission check allows attacker with developer role to perform various deletions.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13341.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/239348
- https://hackerone.com/reports/960244
- https://nvd.nist.gov/vuln/detail/CVE-2020-13341
