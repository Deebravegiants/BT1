# [C] Inefficient Regular Expression Complexity in koa

## Summary
Severity: Critical
Advisory: GHSA-593f-38f6-jp5m
CVE: CVE-2025-25200
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H (CVSS_V4)
Published: 2025-02-12
Source: https://github.com/advisories/GHSA-593f-38f6-jp5m
Type: github-advisory

## Affected
- npm: `koa` — affected >=2.0.0 <2.15.4
- npm: `koa` — affected >=3.0.0-alpha.0 <3.0.0-alpha.3
- npm: `koa` — affected >=1.0.0 <1.7.1
- npm: `koa` — affected >=0 <0.21.2

## Details
### Summary
Koa uses an evil regex to parse the `X-Forwarded-Proto` and `X-Forwarded-Host` HTTP headers. This can be exploited to carry out a Denial-of-Service attack.

### PoC

Coming soon.

### Impact
This is a Regex Denial-of-Service attack and causes memory exhaustion. The regex should be improved and empty values should not be allowed.

## References
- https://github.com/koajs/koa/security/advisories/GHSA-593f-38f6-jp5m
- https://nvd.nist.gov/vuln/detail/CVE-2025-25200
- https://github.com/koajs/koa/commit/5054af6e31ffd451a4151a1fe144cef6e5d0d83c
- https://github.com/koajs/koa/commit/5f294bb1c7c8d9c61904378d250439a321bffd32
- https://github.com/koajs/koa/commit/93fe903fc966635a991bcf890cfc3427d33a1a08
- https://github.com/koajs/koa
- https://github.com/koajs/koa/releases/tag/2.15.4
