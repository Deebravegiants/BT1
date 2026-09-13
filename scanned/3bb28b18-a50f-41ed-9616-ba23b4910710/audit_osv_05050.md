# [H] BIT-gitlab-2021-22214

## Summary
Severity: High
Advisory: BIT-gitlab-2021-22214
Aliases: CVE-2021-22214
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22214
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.12.0 <13.12.2

## Details
When requests to the internal network for webhooks are enabled, a server-side request forgery vulnerability in GitLab CE/EE affecting all versions starting from 10.5 was possible to exploit for an unauthenticated attacker even on a GitLab instance where registration is limited

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22214.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/322926
- https://hackerone.com/reports/1110131
- https://nvd.nist.gov/vuln/detail/CVE-2021-22214
