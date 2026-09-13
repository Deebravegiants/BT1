# [H] Grav < 1.0.6 API Key Scope Bypass via ApiKeyAuthenticator

## Summary
Severity: High
Advisory: CVE-2026-62231
Aliases: CVE-2026-62667, GHSA-x7hm-jc32-v39j
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62231
Type: osv

## Details
The Grav API plugin (getgrav/grav-plugin-api) before 1.0.6 contains an authorization bypass: API keys can be created with a restricted scopes array, but the ApiKeyAuthenticator class never reads or enforces these scopes. It loads and returns the owning user's full account object, so a key created with limited scopes (e.g. read-only) can perform any write, delete, or administrative operation the owning user is authorized for. Fixed in 1.0.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62231.json
- https://github.com/getgrav/grav/security/advisories/GHSA-x7hm-jc32-v39j
- https://nvd.nist.gov/vuln/detail/CVE-2026-62231
- https://www.vulncheck.com/advisories/grav-api-key-scope-bypass-via-apikeyauthenticator
- https://github.com/getgrav/grav
