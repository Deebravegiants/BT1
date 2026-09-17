# [M] BIT-gitlab-2023-1178

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-1178
Aliases: CVE-2023-1178
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-1178
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.11.0 <15.11.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions from 8.6 before 15.9.6, all versions starting from 15.10 before 15.10.5, all versions starting from 15.11 before 15.11.1. File integrity may be compromised when source code or installation packages are pulled from a tag or from a release containing a ref to another commit.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-1178.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/381815
- https://hackerone.com/reports/1778009
- https://nvd.nist.gov/vuln/detail/CVE-2023-1178
