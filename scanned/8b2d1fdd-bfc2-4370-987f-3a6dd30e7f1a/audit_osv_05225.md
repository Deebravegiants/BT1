# [M] BIT-gitlab-2022-2227

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-2227
Aliases: CVE-2022-2227
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2227
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.1.0 <15.1.1

## Details
Improper access control in the runner jobs API in GitLab CE/EE affecting all versions prior to 14.10.5, 15.0 prior to 15.0.4, and 15.1 prior to 15.1.1 allows a previous maintainer of a project with a specific runner to access job and project meta data under certain conditions

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2227.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/300842
- https://hackerone.com/reports/1092199
- https://nvd.nist.gov/vuln/detail/CVE-2022-2227
