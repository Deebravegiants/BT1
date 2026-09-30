# [H] BIT-gitlab-2021-22213

## Summary
Severity: High
Advisory: BIT-gitlab-2021-22213
Aliases: CVE-2021-22213
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22213
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.12.0 <13.12.2

## Details
A cross-site leak vulnerability in the OAuth flow of all versions of GitLab CE/EE since 7.10 allowed an attacker to leak an OAuth access token by getting the victim to visit a malicious page with Safari

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22213.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/300308
- https://hackerone.com/reports/1089277
- https://nvd.nist.gov/vuln/detail/CVE-2021-22213
