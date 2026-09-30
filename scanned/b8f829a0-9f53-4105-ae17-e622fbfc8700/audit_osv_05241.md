# [H] BIT-gitlab-2022-2497

## Summary
Severity: High
Advisory: BIT-gitlab-2022-2497
Aliases: CVE-2022-2497
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2497
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.2.0 <15.2.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 12.6 before 15.0.5, all versions starting from 15.1 before 15.1.4, all versions starting from 15.2 before 15.2.1. A malicious developer could exfiltrate an integration's access token by modifying the integration URL such that authenticated requests are sent to an attacker controlled server.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2497.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/362671
- https://hackerone.com/reports/1557992
- https://nvd.nist.gov/vuln/detail/CVE-2022-2497
