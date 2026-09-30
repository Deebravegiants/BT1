# [M] Hono has Body Limit Middleware Bypass

## Summary
Severity: Medium
Advisory: GHSA-92vj-g62v-jqhh
CVE: CVE-2025-59139
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-09-12
Source: https://github.com/advisories/GHSA-92vj-g62v-jqhh
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.9.7

## Details
### Summary
A flaw in the `bodyLimit` middleware could allow bypassing the configured request body size limit when conflicting HTTP headers were present.

### Details
The middleware previously prioritized the `Content-Length` header even when a `Transfer-Encoding: chunked` header was also included. According to the HTTP specification, `Content-Length` must be ignored in such cases. This discrepancy could allow oversized request bodies to bypass the configured limit.

Most standards-compliant runtimes and reverse proxies may reject such malformed requests with `400 Bad Request`, so the practical impact depends on the runtime and deployment environment.

### Impact
If body size limits are used as a safeguard against large or malicious requests, this flaw could allow attackers to send oversized request bodies. The primary risk is denial of service (DoS) due to excessive memory or CPU consumption when handling very large requests.

### Resolution
The implementation has been updated to align with the HTTP specification, ensuring that `Transfer-Encoding` takes precedence over `Content-Length`. The issue is fixed in Hono v4.9.7, and all users should upgrade immediately.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-92vj-g62v-jqhh
- https://nvd.nist.gov/vuln/detail/CVE-2025-59139
- https://github.com/honojs/hono/commit/605c70560b52f13af10379f79b76717042fafe8d
- https://github.com/honojs/hono
