# [M] BIT-gitlab-2021-39883

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39883
Aliases: CVE-2021-39883
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39883
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.3.0 <14.3.1

## Details
Improper authorization checks in all versions of GitLab EE starting from 13.11 before 14.1.7, all versions starting from 14.2 before 14.2.5, and all versions starting from 14.3 before 14.3.1 allows subgroup members to see epics from all parent subgroups.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39883.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/334279
- https://nvd.nist.gov/vuln/detail/CVE-2021-39883
