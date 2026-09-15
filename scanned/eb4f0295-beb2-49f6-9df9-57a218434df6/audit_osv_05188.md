# [M] BIT-gitlab-2022-1120

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-1120
Aliases: CVE-2022-1120
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1120
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.9.0 <14.9.2

## Details
Missing filtering in an error message in GitLab CE/EE affecting all versions prior to 14.7.7, 14.8 prior to 14.8.5, and 14.9 prior to 14.9.2 exposed sensitive information when an include directive fails in the CI/CD configuration.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1120.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/343466
- https://hackerone.com/reports/1408731
- https://nvd.nist.gov/vuln/detail/CVE-2022-1120
