# [M] BIT-gitlab-2022-3482

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-3482
Aliases: CVE-2022-3482
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3482
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.6.0 <15.6.1

## Details
An improper access control issue in GitLab CE/EE affecting all versions from 11.3 prior to 15.3.5, 15.4 prior to 15.4.4, and 15.5 prior to 15.5.2 allowed an unauthorized user to see release names even when releases we set to be restricted to project members only

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3482.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/377802
- https://hackerone.com/reports/1725841
- https://nvd.nist.gov/vuln/detail/CVE-2022-3482
