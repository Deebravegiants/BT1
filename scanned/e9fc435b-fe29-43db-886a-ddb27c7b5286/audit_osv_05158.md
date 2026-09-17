# [M] BIT-gitlab-2022-0123

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-0123
Aliases: CVE-2022-0123
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0123
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.6.0 <14.6.1

## Details
An issue has been discovered affecting GitLab versions prior to 14.4.5, between 14.5.0 and 14.5.3, and between 14.6.0 and 14.6.1. GitLab does not validate SSL certificates for some of external CI services which makes it possible to perform MitM attacks on connections to these external services.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0123.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/296632
- https://nvd.nist.gov/vuln/detail/CVE-2022-0123
