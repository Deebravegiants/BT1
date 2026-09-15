# [H] BIT-gitlab-2021-22171

## Summary
Severity: High
Advisory: BIT-gitlab-2021-22171
Aliases: CVE-2021-22171
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22171
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.7.0 <13.7.2

## Details
Insufficient validation of authentication parameters in GitLab Pages for GitLab 11.5+ allows an attacker to steal a victim's API token if they click on a maliciously crafted link

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22171.json
- https://gitlab.com/gitlab-org/gitlab-pages/-/issues/262
- https://hackerone.com/reports/718460
- https://nvd.nist.gov/vuln/detail/CVE-2021-22171
