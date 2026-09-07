# [M] Fastify: Incorrect Content-Type parsing can lead to CSRF attack 

## Summary
Severity: Medium
Advisory: GHSA-3fjj-p79j-c9hh
CVE: CVE-2022-41919
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-3fjj-p79j-c9hh
Type: github-advisory

## Affected
- npm: `fastify` — affected >=4.0.0 <4.10.2
- npm: `fastify` — affected >=3.0.0 <3.29.4

## Details
### Impact

The attacker can use the incorrect `Content-Type` to bypass the `Pre-Flight` checking of `fetch`. `fetch()` requests with Content-Type’s [essence](https://mimesniff.spec.whatwg.org/#mime-type-essence) as "application/x-www-form-urlencoded", "multipart/form-data", or "text/plain", could potentially be used to invoke routes that only accepts `application/json` content type, thus bypassing any [CORS protection](https://fetch.spec.whatwg.org/#simple-header), and therefore they could lead to a  Cross-Site Request Forgery attack.

### Patches
For `4.x` users, please update to at least `4.10.2`
For `3.x` users, please update to at least `3.29.4`

### Workarounds

Implement Cross-Site Request Forgery protection using [`@fastify/csrf`](https://www.npmjs.com/package/@fastify/csrf).

### References

Check out the HackerOne report: https://hackerone.com/reports/1763832.

### For more information

[Fastify security policy](https://github.com/fastify/fastify/security/policy)

## References
- https://github.com/fastify/fastify/security/advisories/GHSA-3fjj-p79j-c9hh
- https://nvd.nist.gov/vuln/detail/CVE-2022-41919
- https://github.com/fastify/fastify/commit/62dde76f1f7aca76e38625fe8d983761f26e6fc9
- https://github.com/fastify/fastify
- https://www.npmjs.com/package/@fastify/csrf
