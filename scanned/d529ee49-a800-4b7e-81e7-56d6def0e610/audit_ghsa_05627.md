# [H] SvelteKit is vulnerable to denial of service and possible SSRF when using prerendering

## Summary
Severity: High
Advisory: GHSA-j62c-4x62-9r35
CVE: CVE-2025-67647
CWE: CWE-248, CWE-400, CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:H/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-01-15
Source: https://github.com/advisories/GHSA-j62c-4x62-9r35
Type: github-advisory

## Affected
- npm: `@sveltejs/kit` — affected >=2.19.0 <2.49.5
- npm: `@sveltejs/adapter-node` — affected >=5.4.1 <5.5.1

## Details
### Summary

Versions of SvelteKit are vulnerable to a server side request forgery (SSRF) and denial of service (DoS) under certain conditions.

### Details

Affected versions from 2.44.0 onwards are vulnerable to DoS if:

- your app has at least one prerendered route (`export const prerender = true`)

Affected versions from 2.19.0 onwards are vulnerable to DoS and SSRF if:

- your app has at least one prerendered route (`export const prerender = true`)
- AND you are using `adapter-node` without a configured `ORIGIN` environment variable, and you are not using a reverse proxy that implements Host header validation

### Impact

The DoS causes the running server process to end.

The SSRF allows access to internal services that can be reached without authentication when fetched from SvelteKit's server runtime.

It is also possible to obtain an SXSS via cache poisoning, by forcing a potential CDN to cache an XSS returned by the attacker's server (the latter being able to specify the cache-control of their choice).

### Credits
- Allam Rachid ([zhero;](https://zhero-web-sec.github.io/research-and-things/))
- Allam Yasser (inzo)
- d-xuan ([wednesday](https://d-xuan.github.io/wednesday/))

## References
- https://github.com/sveltejs/kit/security/advisories/GHSA-j62c-4x62-9r35
- https://nvd.nist.gov/vuln/detail/CVE-2025-67647
- https://github.com/sveltejs/kit/commit/d9ae9b00b14f5574d109f3fd548f960594346226
- https://github.com/sveltejs/kit
- https://github.com/sveltejs/kit/releases/tag/%40sveltejs%2Fadapter-node%405.5.1
- https://github.com/sveltejs/kit/releases/tag/%40sveltejs%2Fkit%402.49.5
