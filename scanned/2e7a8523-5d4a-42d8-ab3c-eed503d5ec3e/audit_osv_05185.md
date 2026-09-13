# [M] BIT-gitlab-2022-1099

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-1099
Aliases: CVE-2022-1099
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1099
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.9.0 <14.9.2

## Details
Adding a very large number of tags to a runner in GitLab CE/EE affecting all versions prior to 14.7.7, 14.8 prior to 14.8.5, and 14.9 prior to 14.9.2 allows an attacker to impact the performance of GitLab

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1099.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/328593
- https://nvd.nist.gov/vuln/detail/CVE-2022-1099
