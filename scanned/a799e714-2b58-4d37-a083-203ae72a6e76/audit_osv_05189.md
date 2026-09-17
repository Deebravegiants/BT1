# [M] BIT-gitlab-2022-1121

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-1121
Aliases: CVE-2022-1121
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1121
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.9.0 <14.9.2

## Details
A lack of appropriate timeouts in GitLab Pages included in GitLab CE/EE all versions prior to 14.7.7, 14.8 prior to 14.8.5, and 14.9 prior to 14.9.2 allows an attacker to cause unlimited resource consumption.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1121.json
- https://gitlab.com/gitlab-org/gitlab-pages/-/issues/684
- https://nvd.nist.gov/vuln/detail/CVE-2022-1121
