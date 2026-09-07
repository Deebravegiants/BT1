# [M] fastify vulnerable to X-Forwarded-* spoofing under trustProxy hop-count

## Summary
Severity: Medium
Advisory: GHSA-3m5p-2c4r-xxw2
CVE: CVE-2026-16732
CWE: CWE-348
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-3m5p-2c4r-xxw2
Type: github-advisory

## Affected
- npm: `fastify` — affected >=5.8.3 <5.12.1

## Details
## Impact

The fix for [CVE-2026-3635](https://www.cve.org/CVERecord?id=CVE-2026-3635) ([GHSA-444r-cwp2-x5xf](https://github.com/fastify/fastify/security/advisories/GHSA-444r-cwp2-x5xf)) added a `proxyFn(socket.remoteAddress, 0)` guard on the `X-Forwarded-*` reads in `request.host`, `request.protocol`, `request.hostname`, `request.ip`, and `request.ips`. That guard closes the IP, CIDR, and custom-function forms of `trustProxy` correctly because those forms compile to predicates that inspect the connecting address. The hop-count form (`trustProxy: <number>`) compiles to a predicate that structurally ignores the address argument, so the guard reduces to `0 < tp`, always true for any `tp >= 1`.

Applications configured with `trustProxy: <number>` (documented as "behind N reverse proxies", `trustProxy: 1` being the canonical single-proxy setting) remain vulnerable. An attacker who can reach the Fastify origin directly, bypassing the front-facing proxy, can spoof the request fields exactly as in the unpatched version. Impact class matches the parent CVE-2026-3635: host injection in generated URLs, HTTPS-enforcement bypass, secure-cookie / CSRF-origin bypass, host-based routing and cache poisoning.

## Patches

Patched in fastify 5.12.1. The numeric form of `trustProxy` is now disabled at runtime and removed from the TypeScript type union.

## Workarounds

- Migrate to an IP / CIDR / custom-function `trustProxy` value that validates the connecting address. Custom functions must inspect the `address` argument, not only the hop index.
- Ensure the Fastify origin is only reachable through the trusted proxy chain (no direct network path).

## References
- https://github.com/fastify/fastify/security/advisories/GHSA-3m5p-2c4r-xxw2
- https://nvd.nist.gov/vuln/detail/CVE-2026-16732
- https://github.com/fastify/fastify/commit/8acfea7eada05383a7357e3eb21c2628416df280
- https://cna.openjsf.org/security-advisories.html
- https://github.com/fastify/fastify
- https://github.com/fastify/fastify/releases/tag/v5.12.1
