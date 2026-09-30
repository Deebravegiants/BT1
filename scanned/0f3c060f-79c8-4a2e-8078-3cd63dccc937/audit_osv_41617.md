# [M] Grav < 1.0.0-rc.16 CORS Misconfiguration via API Plugin

## Summary
Severity: Medium
Advisory: CVE-2026-62387
Aliases: CVE-2026-63407, GHSA-93px-98wh-6fj2
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62387
Type: osv

## Details
The Grav API plugin (getgrav/grav-plugin-api) before 1.0.0-rc.16 shipped Access-Control-Allow-Origin: * as its default CORS configuration on all responses, including authenticated endpoints and preflight (OPTIONS) responses. Because the plugin accepts credentials via the Authorization and X-API-Token headers (set programmatically by JavaScript rather than via cookies), an attacker who obtains a valid access token (e.g., via log leakage, Referer headers, browser history, or network capture) can issue fully authenticated cross-origin requests from any malicious website to read sensitive data and perform write operations as the token's user. Fixed in 1.0.0-rc.16.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62387.json
- https://github.com/getgrav/grav/security/advisories/GHSA-93px-98wh-6fj2
- https://nvd.nist.gov/vuln/detail/CVE-2026-62387
- https://www.vulncheck.com/advisories/grav-rc-16-cors-misconfiguration-via-api-plugin
- https://github.com/getgrav/grav
