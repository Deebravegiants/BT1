# [C] BIT-gitlab-2021-22175

## Summary
Severity: Critical
Advisory: BIT-gitlab-2021-22175
Aliases: CVE-2021-22175
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22175
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.8.0 <13.8.4

## Details
When requests to the internal network for webhooks are enabled, a server-side request forgery vulnerability in GitLab affecting all versions starting from 10.5 was possible to exploit for an unauthenticated attacker even on a GitLab instance where registration is disabled

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22175.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/294178
- https://hackerone.com/reports/1059596
- https://nvd.nist.gov/vuln/detail/CVE-2021-22175
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2021-22175
