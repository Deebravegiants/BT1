# [M] BIT-gitlab-2021-39903

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39903
Aliases: CVE-2021-39903
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39903
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.4.0 <14.4.1

## Details
In all versions of GitLab CE/EE since version 13.0, a privileged user, through an API call, can change the visibility level of a group or a project to a restricted option even after the instance administrator sets that visibility option as restricted in settings.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39903.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/300017
- https://hackerone.com/reports/1086781
- https://nvd.nist.gov/vuln/detail/CVE-2021-39903
