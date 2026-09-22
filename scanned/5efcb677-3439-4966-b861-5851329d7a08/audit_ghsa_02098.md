# [H] Cross-site Request Forgery in fastify-csrf

## Summary
Severity: High
Advisory: GHSA-49wp-qq6x-g2rf
CVE: CVE-2020-28482
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-01-20
Source: https://github.com/advisories/GHSA-49wp-qq6x-g2rf
Type: github-advisory

## Affected
- npm: `fastify-csrf` — affected >=0 <3.0.0

## Details
The package fastify-csrf before 3.0.0 has a set of issues that affect its ability to do CSRF protection.
1. The generated cookie used insecure defaults, and did not have the httpOnly flag on: `cookieOpts: { path: '/', sameSite: true }`
2. The CSRF token was available in the GET query parameter

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28482
- https://github.com/fastify/fastify-csrf/pull/26
- https://github.com/fastify/fastify-csrf/commit/3c9de36e9e73ce0eda9207f84f2ac0243e1f5253
- https://github.com/fastify/fastify-csrf
- https://snyk.io/vuln/SNYK-JS-FASTIFYCSRF-1062044
- https://www.npmjs.com/package/fastify-csrf
