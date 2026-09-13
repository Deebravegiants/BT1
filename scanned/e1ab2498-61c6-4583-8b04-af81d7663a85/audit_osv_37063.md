# [H] HomeBox has an Auth Rate Limit Bypass via IP Spoofing

## Summary
Severity: High
Advisory: CVE-2026-27981
Aliases: GHSA-j86g-v96v-jpp3
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-03-03
Source: https://osv.dev/vulnerability/CVE-2026-27981
Type: osv

## Details
HomeBox is a home inventory and organization system. Prior to 0.24.0, the authentication rate limiter (authRateLimiter) tracks failed attempts per client IP. It determines the client IP by reading, 1. X-Real-IP header, 2. First entry of X-Forwarded-For header, and 3. r.RemoteAddr (TCP connection address). These headers were read unconditionally. An attacker connecting directly to Homebox could forge any value in X-Real-IP, effectively getting a fresh rate limit identity per request. There is a TrustProxy option in the configuration (Options.TrustProxy, default false), but this option was never read by any middleware or rate limiter code. Additionally, chi's middleware.RealIP was applied unconditionally in main.go, overwriting r.RemoteAddr with the forged header value before it reaches any handler. This vulnerability is fixed in 0.24.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27981.json
- https://github.com/sysadminsmedia/homebox/security/advisories/GHSA-j86g-v96v-jpp3
- https://nvd.nist.gov/vuln/detail/CVE-2026-27981
