# [M] BIT-gitlab-2022-1999

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-1999
Aliases: CVE-2022-1999
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1999
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.1.0 <15.1.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions from 8.13 prior to 14.10.5, 15.0 prior to 15.0.4, and 15.1 prior to 15.1.1. Under certain conditions, using the REST API an unprivileged user was able to change labels description.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1999.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/357963
- https://nvd.nist.gov/vuln/detail/CVE-2022-1999
