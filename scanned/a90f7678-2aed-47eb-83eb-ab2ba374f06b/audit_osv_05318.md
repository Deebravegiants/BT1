# [M] BIT-gitlab-2022-4315

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-4315
Aliases: CVE-2022-4315
Ecosystem: Bitnami
Published: 2024-11-05
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-4315
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=2.0.0 <3.0.55

## Details
An issue has been discovered in GitLab DAST analyzer affecting all versions starting from 2.0 before 3.0.55, which sends custom request headers with every request on the authentication page.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-4315.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/384995
- https://hackerone.com/reports/1767525
