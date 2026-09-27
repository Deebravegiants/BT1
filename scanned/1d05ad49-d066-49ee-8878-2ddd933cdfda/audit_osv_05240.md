# [M] BIT-gitlab-2022-2456

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-2456
Aliases: CVE-2022-2456
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2456
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.2.0 <15.2.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions before 15.0.5, all versions starting from 15.1 before 15.1.4, all versions starting from 15.2 before 15.2.1. It may be possible for malicious group or project maintainers to change their corresponding group or project visibility by crafting a malicious POST request.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2456.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/359910
- https://hackerone.com/reports/1536559
- https://nvd.nist.gov/vuln/detail/CVE-2022-2456
