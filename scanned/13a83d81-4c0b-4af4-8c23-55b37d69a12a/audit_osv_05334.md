# [M] BIT-gitlab-2023-0483

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-0483
Aliases: CVE-2023-0483
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-0483
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.9.0 <15.9.2

## Details
An issue has been discovered in GitLab affecting all versions starting from 12.1 before 15.7.8, all versions starting from 15.8 before 15.8.4, all versions starting from 15.9 before 15.9.2. It was possible for a project maintainer to extract a Datadog integration API key by modifying the site.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-0483.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/389188
- https://hackerone.com/reports/1836466
- https://nvd.nist.gov/vuln/detail/CVE-2023-0483
