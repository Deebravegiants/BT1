# [C] Grav API Plugin: Missing authorization on API-key generate/revoke lets any admin.login user forge keys for any account

## Summary
Severity: Critical
Advisory: CVE-2026-64852
Aliases: CVE-2026-65007, GHSA-7v74-m76q-8wf3
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-64852
Type: osv

## Details
Grav API Plugin is a RESTful API for Grav CMS that provides full headless access to your site's content. Prior to 1.0.8, the Grav API plugin intercepts the apiKeyGenerate and apiKeyRevoke admin tasks in user/plugins/api/api.php and authorizes the caller with only admin.login. A basic panel user can select another account from the route, create a persistent ApiKeyManager credential bound to that target, and inherit the target's API permissions, including api.super or administrative write access when present. This issue is fixed in version 1.0.8.

## References
- https://github.com/getgrav/grav-plugin-api/releases/tag/1.0.8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64852.json
- https://github.com/getgrav/grav/security/advisories/GHSA-7v74-m76q-8wf3
- https://nvd.nist.gov/vuln/detail/CVE-2026-64852
- https://github.com/getgrav/grav-plugin-api/commit/ed16f0aaa9b398c6f179fb8f51e0fa53e4ed8a30
