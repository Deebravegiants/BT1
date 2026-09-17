# [M] BIT-gitlab-2022-1148

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-1148
Aliases: CVE-2022-1148
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1148
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.9.0 <14.9.2

## Details
Improper authorization in GitLab Pages included with GitLab CE/EE affecting all versions from 11.5 prior to 14.7.7, 14.8 prior to 14.8.5, and 14.9 prior to 14.9.2 allowed an attacker to steal a user's access token on an attacker-controlled private GitLab Pages website and reuse that token on the victim's other private websites

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1148.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/350687
- https://hackerone.com/reports/1439552
- https://nvd.nist.gov/vuln/detail/CVE-2022-1148
