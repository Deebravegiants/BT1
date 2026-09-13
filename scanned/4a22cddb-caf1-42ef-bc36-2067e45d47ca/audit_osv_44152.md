# [C] TarsWeb through 3.0.14 Authentication Bypass via Spoofed X-Forwarded-For and uid Parameter

## Summary
Severity: Critical
Advisory: CVE-2026-80349
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80349
Type: osv

## Details
TarsWeb decides whether a request comes from a trusted local caller using a client-controlled header. app.js sets Koa's proxy option to true without naming which upstream proxies may be trusted and without limiting the number of forwarded hops, so the request address Koa reports is taken from the X-Forwarded-For header supplied by the caller. In midware/ssoMidware.js a single branch covers both the ignored-path list and the ignoreIps allowlist from config/loginConf.js, which contains the loopback address, and that branch assigns the effective account identity from the uid query parameter before falling through to the request without validating any ticket, cookie or password. A request carrying a forged X-Forwarded-For value naming the loopback address and a uid naming an existing account therefore reaches every route the console mounts as that account, including an administrator, with no credential of any kind. Those routes include user and role administration, service configuration, and package upload and deployment. Version 3.0.16 separates the two branches so that a match on the address allowlist assigns the configured default account rather than one named by the caller.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80349.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80349
- https://www.vulncheck.com/advisories/tarsweb-through-3.0.14-authentication-bypass-via-spoofed-x-forwarded-for-and-uid-parameter
- https://github.com/TarsCloud/TarsWeb/issues/212
- https://github.com/TarsCloud/TarsWeb
- https://github.com/TarsCloud/TarsWeb/blob/v3.0.14/app.js
- https://github.com/TarsCloud/TarsWeb/blob/v3.0.14/midware/ssoMidware.js
