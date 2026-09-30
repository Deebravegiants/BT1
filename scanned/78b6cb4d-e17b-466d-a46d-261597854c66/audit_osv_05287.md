# [M] BIT-gitlab-2022-3483

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-3483
Aliases: CVE-2022-3483
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3483
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.5.0 <15.5.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 12.1 before 15.3.5, all versions starting from 15.4 before 15.4.4, all versions starting from 15.5 before 15.5.2. A malicious maintainer could exfiltrate a Datadog integration's access token by modifying the integration URL such that authenticated requests are sent to an attacker controlled server.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3483.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/377799
- https://hackerone.com/reports/1724402
- https://nvd.nist.gov/vuln/detail/CVE-2022-3483
