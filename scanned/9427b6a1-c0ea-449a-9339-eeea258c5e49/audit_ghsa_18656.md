# [M] Hono vulnerable to Vary Header Injection leading to potential CORS Bypass

## Summary
Severity: Medium
Advisory: GHSA-q7jf-gf43-6x6p
CWE: CWE-444
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-24
Source: https://github.com/advisories/GHSA-q7jf-gf43-6x6p
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.10.3

## Details
### Summary  
A flaw in the CORS middleware allowed request `Vary` headers to be reflected into the response, enabling attacker-controlled `Vary` values and potentially affecting cache behavior.

### Details  
The middleware previously copied the `Vary` header from the request when `origin` was not set to `"*"`.  Since `Vary` is a response header that should only be managed by the server, this could allow an attacker to influence caching behavior or cause inconsistent CORS handling.

Most environments will see impact only when shared caches or proxies rely on the `Vary` header. The practical effect varies by configuration.

### Impact  
May cause cache key pollution and inconsistent CORS enforcement in certain setups. No direct confidentiality, integrity, or availability impact in default configurations.  

### Resolution  
Update to the latest patched release. The CORS middleware has been corrected to handle `Vary` exclusively as a response header.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-q7jf-gf43-6x6p
- https://github.com/honojs/hono/commit/d9b8b4b73b4f997994f2764013207365fe711282
- https://github.com/honojs/hono
