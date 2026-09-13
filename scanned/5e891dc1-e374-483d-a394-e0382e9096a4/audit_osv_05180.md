# [C] BIT-gitlab-2022-0735

## Summary
Severity: Critical
Advisory: BIT-gitlab-2022-0735
Aliases: CVE-2022-0735
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0735
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.8.0 <14.8.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 12.10 before 14.6.5, all versions starting from 14.7 before 14.7.4, all versions starting from 14.8 before 14.8.2. An unauthorised user was able to steal runner registration tokens through an information disclosure vulnerability using quick actions commands.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0735.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/353529
- https://nvd.nist.gov/vuln/detail/CVE-2022-0735
