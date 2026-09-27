# [M] BIT-gitlab-2022-2882

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-2882
Aliases: CVE-2022-2882
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2882
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.4.0 <15.4.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 12.6 before 15.2.5, all versions starting from 15.3 before 15.3.4, all versions starting from 15.4 before 15.4.1. A malicious maintainer could exfiltrate a GitHub integration's access token by modifying the integration URL such that authenticated requests are sent to an attacker controlled server.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2882.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/371082
- https://hackerone.com/reports/1656722
- https://nvd.nist.gov/vuln/detail/CVE-2022-2882
