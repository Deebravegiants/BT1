# [M] BIT-gitlab-2022-1460

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-1460
Aliases: CVE-2022-1460
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1460
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.10.0 <14.10.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 9.2 before 14.8.6, all versions starting from 14.9 before 14.9.4, all versions starting from 14.10 before 14.10.1. GitLab was not performing correct authorizations on scheduled pipelines allowing a malicious user to run a pipeline in the context of another user.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1460.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/118782
- https://hackerone.com/reports/755078
- https://nvd.nist.gov/vuln/detail/CVE-2022-1460
