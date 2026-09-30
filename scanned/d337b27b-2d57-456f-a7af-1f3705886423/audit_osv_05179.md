# [M] BIT-gitlab-2022-0549

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-0549
Aliases: CVE-2022-0549
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0549
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.5.0 <14.5.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions before 14.3.6, all versions starting from 14.4 before 14.4.4, all versions starting from 14.5 before 14.5.2. Under certain conditions, GitLab REST API may allow unprivileged users to add other users to groups even if that is not possible to do through the Web UI.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0549.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/342448
- https://nvd.nist.gov/vuln/detail/CVE-2022-0549
