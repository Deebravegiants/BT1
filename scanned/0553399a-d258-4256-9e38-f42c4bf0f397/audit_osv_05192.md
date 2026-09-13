# [C] BIT-gitlab-2022-1162

## Summary
Severity: Critical
Advisory: BIT-gitlab-2022-1162
Aliases: CVE-2022-1162
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1162
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.9.0 <14.9.2

## Details
A hardcoded password was set for accounts registered using an OmniAuth provider (e.g. OAuth, LDAP, SAML) in GitLab CE/EE versions 14.7 prior to 14.7.7, 14.8 prior to 14.8.5, and 14.9 prior to 14.9.2 allowing attackers to potentially take over accounts

## References
- http://packetstormsecurity.com/files/166828/Gitlab-14.9-Authentication-Bypass.html
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1162.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/357210
- https://nvd.nist.gov/vuln/detail/CVE-2022-1162
