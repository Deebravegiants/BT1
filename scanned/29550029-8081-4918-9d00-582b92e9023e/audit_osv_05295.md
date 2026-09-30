# [M] BIT-gitlab-2022-3706

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-3706
Aliases: CVE-2022-3706
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3706
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.5.0 <15.5.2

## Details
Improper authorization in GitLab CE/EE affecting all versions from 7.14 prior to 15.3.5, 15.4 prior to 15.4.4, and 15.5 prior to 15.5.2 allows a user retrying a job in a downstream pipeline to take ownership of the retried jobs in the upstream pipeline even if the user doesn't have access to that project.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3706.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/365532
- https://nvd.nist.gov/vuln/detail/CVE-2022-3706
