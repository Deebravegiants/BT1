# [H] BIT-gitlab-2022-0425

## Summary
Severity: High
Advisory: BIT-gitlab-2022-0425
Aliases: CVE-2022-0425
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0425
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.7.0 <14.7.1

## Details
A DNS rebinding vulnerability in the Irker IRC Gateway integration in all versions of GitLab CE/EE since version 7.9 allows an attacker to trigger Server Side Request Forgery (SSRF) attacks.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0425.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/22350
- https://nvd.nist.gov/vuln/detail/CVE-2022-0425
