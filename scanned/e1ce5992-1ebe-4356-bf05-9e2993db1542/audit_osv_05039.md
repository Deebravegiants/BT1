# [H] BIT-gitlab-2021-22200

## Summary
Severity: High
Advisory: BIT-gitlab-2021-22200
Aliases: CVE-2021-22200
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22200
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.10.0 <13.10.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting with 12.6. Under a special condition it was possible to access data of an internal repository through a public project fork as an anonymous user.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22200.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/247523
- https://nvd.nist.gov/vuln/detail/CVE-2021-22200
