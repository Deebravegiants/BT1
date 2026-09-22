# [H] BIT-gitlab-2021-39867

## Summary
Severity: High
Advisory: BIT-gitlab-2021-39867
Aliases: CVE-2021-39867
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39867
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.3.0 <14.3.1

## Details
In all versions of GitLab CE/EE since version 8.15, a DNS rebinding vulnerability in Gitea Importer may be exploited by an attacker to trigger Server Side Request Forgery (SSRF) attacks.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39867.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/214401
- https://nvd.nist.gov/vuln/detail/CVE-2021-39867
