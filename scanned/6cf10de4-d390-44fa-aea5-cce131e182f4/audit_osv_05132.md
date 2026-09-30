# [M] BIT-gitlab-2021-39914

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39914
Aliases: CVE-2021-39914
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39914
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.4.0 <14.4.1

## Details
A regular expression denial of service issue in GitLab versions 8.13 to 14.2.5, 14.3.0 to 14.3.3 and 14.4.0 could cause excessive usage of resources when a specially crafted username was used when provisioning a new user

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39914.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/289948
- https://nvd.nist.gov/vuln/detail/CVE-2021-39914
