# [M] BIT-gitlab-2022-4376

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-4376
Aliases: CVE-2022-4376
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-4376
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.11.0 <15.11.1

## Details
An issue has been discovered in GitLab affecting all versions before 15.9.6, all versions starting from 15.10 before 15.10.5, all versions starting from 15.11 before 15.11.1. Under certain conditions, an attacker may be able to map a private email of a GitLab user to their GitLab account on an instance.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-4376.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/385246
- https://hackerone.com/reports/1794713
- https://nvd.nist.gov/vuln/detail/CVE-2022-4376
