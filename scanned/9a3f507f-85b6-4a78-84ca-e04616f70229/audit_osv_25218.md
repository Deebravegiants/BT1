# [H] Nextcloud user_oidc app is missing brute force protection

## Summary
Severity: High
Advisory: CVE-2023-32074
Aliases: GHSA-x8mc-84wj-rf34
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-05-25
Source: https://osv.dev/vulnerability/CVE-2023-32074
Type: osv

## Details
user_oidc app is an OpenID Connect user backend for Nextcloud. Authentication can be broken/bypassed in user_oidc app. It is recommended that the Nextcloud user_oidc app is upgraded to 1.3.2

## References
- https://hackerone.com/reports/1954711
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32074.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-x8mc-84wj-rf34
- https://nvd.nist.gov/vuln/detail/CVE-2023-32074
- https://github.com/nextcloud/user_oidc/pull/615
