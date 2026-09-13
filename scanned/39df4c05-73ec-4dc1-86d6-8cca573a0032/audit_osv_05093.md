# [M] BIT-gitlab-2021-39868

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39868
Aliases: CVE-2021-39868
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39868
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.3.0 <14.3.1

## Details
In all versions of GitLab CE/EE since version 8.12, an authenticated low-privileged malicious user may create a project with unlimited repository size by modifying values in a project export.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39868.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/24649
- https://hackerone.com/reports/420258
- https://nvd.nist.gov/vuln/detail/CVE-2021-39868
