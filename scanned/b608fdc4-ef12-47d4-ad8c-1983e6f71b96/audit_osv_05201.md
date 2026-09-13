# [M] BIT-gitlab-2022-1406

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-1406
Aliases: CVE-2022-1406
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1406
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.10.0 <14.10.1

## Details
Improper input validation in GitLab CE/EE affecting all versions from 8.12 prior to 14.8.6, all versions from 14.9.0 prior to 14.9.4, and 14.10.0 allows a Developer to read protected Group or Project CI/CD variables by importing a malicious project

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1406.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/353958
- https://hackerone.com/reports/1485381
- https://nvd.nist.gov/vuln/detail/CVE-2022-1406
