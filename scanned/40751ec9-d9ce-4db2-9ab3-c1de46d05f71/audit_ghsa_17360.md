# [M] fastify-reply-from affected by bypass of reply forwarding

## Summary
Severity: Medium
Advisory: GHSA-2q7r-29rg-6m5h
CVE: CVE-2025-66415
CWE: CWE-441
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-2q7r-29rg-6m5h
Type: github-advisory

## Affected
- npm: `@fastify/reply-from` — affected >=0 <12.5.0

## Details
### Summary
By crafting a malicious URL, an attacker could access routes that are not allowed, even though the `reply.from` is defined for specific routes in `@fastify/reply-from`.

### Details

An attacker can bypass the route defined by the `@fastify/reply-from` package by adding a `..` symbol, which, for `curl` version `8.7.1`, is `%2e%2e`.

### Impact

Everyone is using this package with the routes option to protect a 3rd-party resource.

## References
- https://github.com/fastify/fastify-reply-from/security/advisories/GHSA-2q7r-29rg-6m5h
- https://nvd.nist.gov/vuln/detail/CVE-2025-66415
- https://github.com/fastify/fastify-reply-from/commit/4d9795cd5b57a36756d37b7f036eae369f69fa66
- https://github.com/fastify/fastify-reply-from
