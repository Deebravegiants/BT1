# [M] BIT-gitlab-2022-3279

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-3279
Aliases: CVE-2022-3279
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3279
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.4.0 <15.4.1

## Details
An unhandled exception in job log parsing in GitLab CE/EE affecting all versions prior to 15.2.5, 15.3 prior to 15.3.4, and 15.4 prior to 15.4.1 allows an attacker to prevent access to job logs

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3279.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/364249
- https://hackerone.com/reports/1587261
- https://nvd.nist.gov/vuln/detail/CVE-2022-3279
