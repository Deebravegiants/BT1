# [H] BIT-gitlab-2022-2527

## Summary
Severity: High
Advisory: BIT-gitlab-2022-2527
Aliases: CVE-2022-2527
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2527
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.3.0 <15.3.2

## Details
An issue in Incident Timelines has been discovered in GitLab CE/EE affecting all versions starting from 14.9 before 15.1.6, all versions starting from 15.2 before 15.2.4, all versions starting from 15.3 before 15.3.2.which allowed an authenticated attacker to inject arbitrary content. A victim interacting with this content could lead to arbitrary requests.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2527.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/368676
- https://hackerone.com/reports/1647446
- https://nvd.nist.gov/vuln/detail/CVE-2022-2527
