# [H] Capgo - Authorization Bypass in API Key Management via App-Limited Keys

## Summary
Severity: High
Advisory: CVE-2026-56225
Aliases: GHSA-hwc7-j2p6-43xp
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-56225
Type: osv

## Details
Capgo before 12.128.2 contains an authorization bypass vulnerability in its public API key management handlers (get/put/delete/post). API keys created with mode=all but restricted to a single app via limited_to_apps are only checked for limited_to_orgs and not for limited_to_apps, so an app-scoped key can enumerate, update, and delete sibling API keys belonging to the same account that are outside its declared app scope, enabling tampering with account-level credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56225.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-hwc7-j2p6-43xp
- https://nvd.nist.gov/vuln/detail/CVE-2026-56225
- https://www.vulncheck.com/advisories/capgo-authorization-bypass-in-api-key-management-via-app-limited-keys
